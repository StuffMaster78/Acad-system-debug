from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from loyalty_management.models import (
    ClientBadge,
    LoyaltyTier,
    LoyaltyTransaction,
    Milestone,
)

logger = logging.getLogger(__name__)


class LoyaltyPointsService:
    """
    Single write path for client loyalty point balances.
    """

    @classmethod
    @transaction.atomic
    def award_points(
        cls,
        *,
        client_profile,
        points: int,
        website=None,
        reason: str,
        metadata: dict[str, Any] | None = None,
        notify: bool = True,
    ) -> LoyaltyTransaction:
        if points <= 0:
            raise ValidationError("Points awarded must be greater than zero.")

        resolved_website = website or client_profile.website
        locked_client = cls._lock_client(client_profile)
        locked_client.loyalty_points += points
        locked_client.save(update_fields=["loyalty_points"])

        transaction_obj = LoyaltyTransaction.objects.create(
            website=resolved_website,
            client=locked_client,
            points=points,
            transaction_type="add",
            reason=reason,
        )

        old_tier_id = locked_client.tier_id
        cls.update_tier(client_profile=locked_client)
        cls.award_milestones(client_profile=locked_client)

        locked_client.refresh_from_db(fields=["loyalty_points", "tier"])
        if notify:
            cls._notify_points_awarded(
                client_profile=locked_client,
                website=resolved_website,
                points=points,
                reason=reason,
                transaction_obj=transaction_obj,
                metadata=metadata or {},
            )
            if old_tier_id != locked_client.tier_id and locked_client.tier_id:
                cls._notify_tier_upgraded(
                    client_profile=locked_client,
                    website=resolved_website,
                )

        return transaction_obj

    @classmethod
    @transaction.atomic
    def deduct_points(
        cls,
        *,
        client_profile,
        points: int,
        website=None,
        reason: str,
        transaction_type: str = "redeem",
    ) -> LoyaltyTransaction:
        if points <= 0:
            raise ValidationError("Points deducted must be greater than zero.")

        resolved_website = website or client_profile.website
        locked_client = cls._lock_client(client_profile)

        if locked_client.loyalty_points < points:
            raise ValidationError("Insufficient loyalty points.")

        locked_client.loyalty_points -= points
        locked_client.save(update_fields=["loyalty_points"])

        transaction_obj = LoyaltyTransaction.objects.create(
            website=resolved_website,
            client=locked_client,
            points=-points,
            transaction_type=transaction_type,
            reason=reason,
        )
        cls.update_tier(client_profile=locked_client)
        return transaction_obj

    @classmethod
    @transaction.atomic
    def sync_balance(cls, *, client_profile) -> int:
        locked_client = cls._lock_client(client_profile)
        total = cls.get_total_points(client_profile=locked_client)
        if locked_client.loyalty_points != total:
            locked_client.loyalty_points = max(total, 0)
            locked_client.save(update_fields=["loyalty_points"])
        cls.update_tier(client_profile=locked_client)
        return locked_client.loyalty_points

    @staticmethod
    def get_total_points(*, client_profile) -> int:
        total = client_profile.loyalty_transactions.aggregate(
            total=Sum("points"),
        )["total"]
        return int(total or 0)

    @staticmethod
    def update_tier(*, client_profile) -> None:
        tier = (
            LoyaltyTier.objects.filter(
                website=client_profile.website,
                threshold__lte=client_profile.loyalty_points,
            )
            .order_by("-threshold")
            .first()
        )

        if client_profile.tier_id != getattr(tier, "id", None):
            client_profile.tier = tier
            client_profile.save(update_fields=["tier"])

    @staticmethod
    def award_milestones(*, client_profile) -> None:
        existing_badges = set(
            client_profile.badges.filter(
                badge_name__startswith="Milestone: ",
            ).values_list("badge_name", flat=True),
        )
        milestones = Milestone.objects.filter(
            website=client_profile.website,
            target_type="loyalty_points",
            target_value__lte=client_profile.loyalty_points,
        )

        for milestone in milestones:
            badge_name = f"Milestone: {milestone.name}"
            if badge_name in existing_badges:
                continue

            ClientBadge.objects.create(
                client=client_profile,
                website=client_profile.website,
                badge_name=badge_name,
                description=milestone.description,
            )

            if milestone.reward_points:
                client_profile.loyalty_points += milestone.reward_points
                client_profile.save(update_fields=["loyalty_points"])
                LoyaltyTransaction.objects.create(
                    client=client_profile,
                    website=client_profile.website,
                    points=milestone.reward_points,
                    transaction_type="add",
                    reason=f"Milestone achieved: {milestone.name}",
                )

    @staticmethod
    def _lock_client(client_profile):
        from client_management.models import ClientProfile

        return ClientProfile.objects.select_for_update().get(
            pk=client_profile.pk,
        )

    @staticmethod
    def _notify_points_awarded(
        *,
        client_profile,
        website,
        points: int,
        reason: str,
        transaction_obj,
        metadata: dict[str, Any],
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            NotificationService.notify(
                event_key="loyalty.points_awarded",
                recipient=client_profile.user,
                website=website,
                context={
                    "points": points,
                    "reason": reason,
                    "total_points": client_profile.loyalty_points,
                    "transaction_id": transaction_obj.id,
                    **metadata,
                },
            )
        except Exception as exc:
            logger.warning(
                "Failed to queue loyalty points notification: %s",
                exc,
                exc_info=True,
            )

    @staticmethod
    def _notify_tier_upgraded(*, client_profile, website) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            NotificationService.notify(
                event_key="loyalty.tier_upgraded",
                recipient=client_profile.user,
                website=website,
                context={
                    "tier_name": client_profile.tier.name,
                    "perks": client_profile.tier.perks or "",
                    "total_points": client_profile.loyalty_points,
                },
            )
        except Exception as exc:
            logger.warning(
                "Failed to queue loyalty tier notification: %s",
                exc,
                exc_info=True,
            )
