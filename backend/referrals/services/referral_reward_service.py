from __future__ import annotations

import logging
from decimal import Decimal

from django.db import transaction

from client_management.models import ClientProfile
from loyalty_management.services.points_service import LoyaltyPointsService
from referrals.models import Referral, ReferralBonusConfig
from wallets.constants import WalletEntryType
from wallets.services.client_wallet_service import ClientWalletService
from wallets.services.wallet_service import WalletService

logger = logging.getLogger(__name__)


class ReferralRewardService:
    """
    Coordinates rewards earned when referred clients qualify.

    Referrals own attribution. Loyalty owns points. Wallet owns cash value.
    This service is the bridge between those domains.
    """

    DEFAULT_POINTS_PER_WALLET_UNIT = 10

    @classmethod
    @transaction.atomic
    def award_for_qualifying_order(cls, *, order) -> Referral | None:
        referee = getattr(order, "client", None)
        website = getattr(order, "website", None)
        if referee is None or website is None:
            return None

        referral = (
            Referral.objects.select_for_update()
            .filter(
                website=website,
                referee=referee,
                bonus_awarded=False,
                is_deleted=False,
                is_voided=False,
            )
            .first()
        )
        if referral is None:
            return None

        config = ReferralBonusConfig.objects.filter(website=website).first()
        if config is None:
            return None

        if referral.is_flagged:
            logger.info(
                "Skipping flagged referral reward referral_id=%s",
                referral.id,
            )
            return None

        if not cls._order_qualifies(order=order, config=config):
            return None

        if not cls._is_first_qualifying_order(order=order):
            return None

        wallet_bonus = Decimal(config.first_order_bonus or 0)
        referrer_profile = cls._get_client_profile(
            user=referral.referrer,
            website=website,
        )
        referee_profile = cls._get_client_profile(
            user=referral.referee,
            website=website,
        )

        if config.award_wallet_bonus and wallet_bonus > 0:
            wallet = ClientWalletService.get_wallet(
                website=website,
                client=referral.referrer,
            )
            WalletService.credit_wallet(
                wallet=wallet,
                website=website,
                amount=wallet_bonus,
                entry_type=WalletEntryType.REFERRAL_BONUS,
                description="Referral reward",
                reference=f"referral-{referral.id}",
                reference_type="referral",
                reference_id=str(referral.id),
                metadata={
                    "referral_id": referral.id,
                    "order_id": order.id,
                    "referee_id": referral.referee_id,
                    "note": f"Referral reward for order #{order.id}",
                },
            )

        if config.award_loyalty_points and referrer_profile is not None:
            referrer_points = cls._resolve_referrer_points(config=config)
            if referrer_points > 0:
                LoyaltyPointsService.award_points(
                    client_profile=referrer_profile,
                    website=website,
                    points=referrer_points,
                    reason=f"Referral reward for order #{order.id}",
                    metadata={
                        "referral_id": referral.id,
                        "order_id": order.id,
                        "referee_id": referral.referee_id,
                    },
                )

        if config.award_loyalty_points and referee_profile is not None:
            if config.referee_loyalty_points > 0:
                LoyaltyPointsService.award_points(
                    client_profile=referee_profile,
                    website=website,
                    points=config.referee_loyalty_points,
                    reason="Referral signup reward",
                    metadata={
                        "referral_id": referral.id,
                        "order_id": order.id,
                        "referrer_id": referral.referrer_id,
                    },
                )

        referral.bonus_awarded = True
        referral.first_order_bonus_credited = True
        referral.save(
            update_fields=[
                "bonus_awarded",
                "first_order_bonus_credited",
            ],
        )

        cls._notify_referral_reward(
            referral=referral,
            order=order,
            wallet_bonus=wallet_bonus,
            loyalty_points=(
                cls._resolve_referrer_points(config=config)
                if config.award_loyalty_points
                else 0
            ),
        )
        return referral

    @staticmethod
    def _get_client_profile(*, user, website):
        return ClientProfile.objects.filter(user=user, website=website).first()

    @classmethod
    def _resolve_referrer_points(cls, *, config: ReferralBonusConfig) -> int:
        if config.referrer_loyalty_points:
            return int(config.referrer_loyalty_points)
        return int(Decimal(config.first_order_bonus or 0) * cls.DEFAULT_POINTS_PER_WALLET_UNIT)

    @staticmethod
    def _order_qualifies(*, order, config: ReferralBonusConfig) -> bool:
        qualifying_status = config.qualifying_order_status or "approved"
        if qualifying_status == "approved":
            return getattr(order, "approved_at", None) is not None or getattr(order, "status", None) == "approved"
        if qualifying_status == "completed":
            return getattr(order, "completed_at", None) is not None or getattr(order, "status", None) == "completed"
        return getattr(order, "status", None) == qualifying_status

    @staticmethod
    def _is_first_qualifying_order(*, order) -> bool:
        from orders.models import Order

        return not Order.objects.filter(
            website=order.website,
            client=order.client,
            approved_at__isnull=False,
        ).exclude(pk=order.pk).exists()

    @staticmethod
    def _notify_referral_reward(
        *,
        referral,
        order,
        wallet_bonus: Decimal,
        loyalty_points: int,
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            NotificationService.notify(
                event_key="referral.reward_earned",
                recipient=referral.referrer,
                website=referral.website,
                context={
                    "referral_id": referral.id,
                    "order_id": order.id,
                    "referee_id": referral.referee_id,
                    "wallet_bonus": str(wallet_bonus),
                    "loyalty_points": loyalty_points,
                },
                priority="high",
            )
        except Exception as exc:
            logger.warning(
                "Failed to queue referral reward notification: %s",
                exc,
                exc_info=True,
            )
