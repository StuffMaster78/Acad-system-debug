from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from client_management.models import ClientProfile
from loyalty_management.models import LoyaltyPointsConversionConfig
from loyalty_management.services.points_service import LoyaltyPointsService
from wallets.constants import WalletEntryType
from wallets.services.client_wallet_service import ClientWalletService
from wallets.services.wallet_service import WalletService


class LoyaltyConversionService:
    """
    Compatibility facade for loyalty earning and wallet conversion.

    New point writes should go through LoyaltyPointsService directly. This
    class remains as the public conversion API used by existing views/tasks.
    """

    @staticmethod
    def convert_points_to_wallet(
        client: ClientProfile,
        website,
        points: int,
    ) -> Decimal:
        config = LoyaltyPointsConversionConfig.objects.filter(
            website=website,
            active=True,
        ).first()
        if not config:
            raise ValidationError(
                "Loyalty conversion is not available for this website.",
            )

        if points < config.min_conversion_points:
            raise ValidationError(
                f"Minimum {config.min_conversion_points} points required "
                "to convert.",
            )

        current_balance = LoyaltyPointsService.get_total_points(
            client_profile=client,
        )
        if points > current_balance:
            raise ValidationError("You do not have enough loyalty points.")

        amount = Decimal(points) * config.conversion_rate
        if amount > config.max_conversion_limit:
            raise ValidationError(
                f"Cannot convert more than ${config.max_conversion_limit} "
                "at once.",
            )

        with transaction.atomic():
            LoyaltyPointsService.deduct_points(
                client_profile=client,
                points=points,
                website=website,
                reason="Converted to wallet balance",
            )
            wallet = ClientWalletService.get_wallet(
                website=website,
                client=client.user,
            )
            WalletService.credit_wallet(
                wallet=wallet,
                website=website,
                amount=amount,
                entry_type=WalletEntryType.LOYALTY_CONVERSION,
                description="Loyalty Points Conversion",
                reference=f"loyalty-conversion-{client.id}-{points}",
                reference_type="loyalty_conversion",
                reference_id=str(client.id),
                metadata={"points": points, "note": f"Converted {points} points"},
            )
            LoyaltyConversionService._notify_points_converted(
                client=client,
                website=website,
                points=points,
                amount=amount,
            )

        return amount

    @staticmethod
    def calculate_points(order) -> int:
        config = LoyaltyPointsConversionConfig.objects.filter(
            website=order.website,
            active=True,
        ).first()
        if not config:
            return 0

        total = getattr(order, "total_price", None)
        if total is None:
            total = getattr(order, "total_cost", Decimal("0.00"))

        return int(Decimal(total) * config.points_per_dollar)

    @staticmethod
    def add_points_from_order(order):
        if getattr(order, "status", None) != "completed":
            return None

        client_user = getattr(order, "client", None)
        if client_user is None:
            return None

        client_profile = ClientProfile.objects.filter(
            user=client_user,
            website=order.website,
        ).first()
        if client_profile is None:
            return None

        points = LoyaltyConversionService.calculate_points(order)
        if points <= 0:
            return None

        return LoyaltyPointsService.award_points(
            client_profile=client_profile,
            website=order.website,
            points=points,
            reason=f"Loyalty points for order #{order.id}",
            metadata={"order_id": order.id},
        )

    @staticmethod
    def award_points(client_profile, points, website, reason):
        return LoyaltyPointsService.award_points(
            client_profile=client_profile,
            points=points,
            website=website,
            reason=reason,
        )

    @staticmethod
    def deduct_points(client_profile, points, website, reason):
        return LoyaltyPointsService.deduct_points(
            client_profile=client_profile,
            points=points,
            website=website,
            reason=reason,
        )

    @staticmethod
    def get_total_points(client):
        return LoyaltyPointsService.get_total_points(client_profile=client)

    @staticmethod
    def update_loyalty_tier(client_profile):
        return LoyaltyPointsService.update_tier(client_profile=client_profile)

    @staticmethod
    def check_and_award_milestones(client_profile):
        return LoyaltyPointsService.award_milestones(
            client_profile=client_profile,
        )

    @staticmethod
    def try_auto_convert(client_profile, website):
        config = LoyaltyPointsConversionConfig.objects.filter(
            website=website,
            active=True,
        ).first()
        if not config:
            return None

        points = client_profile.loyalty_points
        if points < config.min_conversion_points:
            return None

        convertible_points = (
            points // config.min_conversion_points
        ) * config.min_conversion_points

        if not convertible_points:
            return None

        return LoyaltyConversionService.convert_points_to_wallet(
            client=client_profile,
            website=website,
            points=convertible_points,
        )

    @staticmethod
    def sync_loyalty_cache(client_profile):
        return LoyaltyPointsService.sync_balance(
            client_profile=client_profile,
        )

    @staticmethod
    def _notify_points_converted(
        *,
        client: ClientProfile,
        website,
        points: int,
        amount: Decimal,
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            client.refresh_from_db(fields=["loyalty_points"])
            NotificationService.notify(
                event_key="loyalty.points_converted",
                recipient=client.user,
                website=website,
                context={
                    "points": points,
                    "amount": str(amount),
                    "total_points": client.loyalty_points,
                },
            )
        except Exception:
            pass
