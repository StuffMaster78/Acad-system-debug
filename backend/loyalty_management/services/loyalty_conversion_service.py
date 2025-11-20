from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from loyalty_management.models import LoyaltyTransaction, LoyaltyPointsConversionConfig
from wallet.models import Wallet  # Assume this exists
from client_management.models import ClientProfile
from django.db import models
from django.utils.translation import gettext_lazy as _
from loyalty_management.models import LoyaltyTier, Milestone, ClientBadge
from client_management.models import ClientProfile
from wallet.services.wallet_transaction_service import WalletTransactionService





class LoyaltyConversionService:
    """Service class to handle loyalty points conversion to wallet balance.
    This class encapsulates the logic for converting loyalty points into wallet balance,
    ensuring that all business rules and validations are applied.
    It includes methods for checking conversion eligibility, performing the conversion,
    and updating the client's loyalty tier based on their total points.
    """

    @staticmethod
    def convert_points_to_wallet(client: ClientProfile, website, points: int):
        config = LoyaltyPointsConversionConfig.objects.filter(website=website, active=True).first()
        if not config:
            raise ValidationError("Loyalty conversion is not available for this website.")

        if points < config.min_conversion_points:
            raise ValidationError(f"Minimum {config.min_conversion_points} points required to convert.")

        current_balance = LoyaltyConversionService.get_total_points(client)
        if points > current_balance:
            raise ValidationError("You do not have enough loyalty points.")

        amount = Decimal(points) * config.conversion_rate

        if amount > config.max_conversion_limit:
            raise ValidationError(f"Cannot convert more than ${config.max_conversion_limit} at once.")

        with transaction.atomic():
            # Deduct loyalty points
            LoyaltyConversionService.deduct_points(
                client_profile=client,
                points=points,
                website=website,
                reason="Converted to wallet balance"
            )

            # Add to wallet
            wallet, _ = Wallet.objects.get_or_create(client=client, website=website)
            wallet.balance += amount
            wallet.save()

            # Optional: Add a WalletTransaction for audit
            wallet.transactions.create(
                amount=amount,
                type="credit",
                source="loyalty_conversion",
                note=f"Converted {points} points"
            )

        return amount
    
    @staticmethod
    def calculate_points(order):
        config = LoyaltyPointsConversionConfig.objects.filter(website=order.website, active=True).first()
        if not config:
            return 0
        return int(order.total_cost * config.points_per_dollar)

    
    @staticmethod
    def add_points_from_order(order):
        if order.status != 'completed':
            return

        client_profile = order.client  # or use lookup if needed
        if not client_profile:
            return

        points = LoyaltyConversionService.calculate_points(order)
        if points <= 0:
            return

        client_profile.loyalty_points += points
        client_profile.save()

        LoyaltyTransaction.objects.create(
            client=client_profile,
            website=order.website,
            points=points,
            transaction_type='add',
            reason=f"Loyalty points for order #{order.id}",
        )

        # Send notification
        try:
            from notifications_system.services.notification_helper import NotificationHelper
            NotificationHelper.notify_loyalty_points_awarded(
                client_profile=client_profile,
                points=points,
                reason=f"Order #{order.id} completed",
                total_points=client_profile.loyalty_points
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send loyalty points notification: {e}")

        LoyaltyConversionService.update_loyalty_tier(client_profile)
        LoyaltyConversionService.check_and_award_milestones(client_profile)


    @staticmethod
    def award_points(client_profile, points, website, reason):
        client_profile.loyalty_points += points
        client_profile.save()

        LoyaltyTransaction.objects.create(
            client=client_profile,
            website=website,
            points=points,
            transaction_type='add',
            reason=reason
        )

        # Send notification
        try:
            from notifications_system.services.notification_helper import NotificationHelper
            NotificationHelper.notify_loyalty_points_awarded(
                client_profile=client_profile,
                points=points,
                reason=reason,
                total_points=client_profile.loyalty_points
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send loyalty points notification: {e}")

        old_tier = client_profile.tier
        LoyaltyConversionService.update_loyalty_tier(client_profile)
        
        # Check if tier was upgraded
        if old_tier != client_profile.tier and client_profile.tier:
            try:
                from notifications_system.services.notification_helper import NotificationHelper
                NotificationHelper.notify_tier_upgraded(
                    client_profile=client_profile,
                    tier_name=client_profile.tier.name,
                    perks=client_profile.tier.perks or ""
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send tier upgrade notification: {e}")
        
        LoyaltyConversionService.check_and_award_milestones(client_profile)
        LoyaltyConversionService.try_auto_convert(client_profile, website)

    @staticmethod
    def get_total_points(client):
        return client.loyalty_transactions.aggregate(
            total=models.Sum('points')
        )['total'] or 0
    
    @staticmethod
    def update_loyalty_tier(client_profile):
        total_points = client_profile.loyalty_points

        tier = LoyaltyTier.objects.filter(
            website=client_profile.website,
            threshold__lte=total_points
        ).order_by('-threshold').first()

        if tier and client_profile.tier != tier:
            client_profile.tier = tier
            client_profile.save()

    @staticmethod
    def check_and_award_milestones(client_profile):
        existing_badges = set(
            client_profile.badges.filter(badge_name__startswith="Milestone: ").values_list('badge_name', flat=True)
        )

        milestones = Milestone.objects.filter(
            website=client_profile.website,
            target_type='loyalty_points',
            target_value__lte=client_profile.loyalty_points
        )

        for milestone in milestones:
            badge_name = f"Milestone: {milestone.name}"
            if badge_name in existing_badges:
                continue

            # Award milestone points
            client_profile.loyalty_points += milestone.reward_points
            client_profile.save()

            # Record badge
            ClientBadge.objects.create(
                client=client_profile,
                website=client_profile.website,
                badge_name=badge_name,
                description=milestone.description
            )

            # Log transaction
            LoyaltyTransaction.objects.create(
                client=client_profile,
                website=client_profile.website,
                points=milestone.reward_points,
                transaction_type='add',
                reason=f"Milestone achieved: {milestone.name}"
            )

    @staticmethod
    def deduct_points(client_profile, points, website, reason):
        if client_profile.loyalty_points < points:
            raise ValidationError("Insufficient loyalty points.")

        client_profile.loyalty_points -= points
        client_profile.save()

        LoyaltyTransaction.objects.create(
            client=client_profile,
            website=website,
            points=-points,
            transaction_type='redeem',
            reason=reason
        )

    @staticmethod
    def convert_points_to_wallet(client: ClientProfile, website, points: int):
        config = LoyaltyPointsConversionConfig.objects.filter(website=website, active=True).first()
        if not config:
            raise ValidationError("Loyalty conversion is not available for this website.")

        if points < config.min_conversion_points:
            raise ValidationError(f"Minimum {config.min_conversion_points} points required to convert.")

        current_balance = LoyaltyConversionService.get_total_points(client)
        if points > current_balance:
            raise ValidationError("You do not have enough loyalty points.")

        amount = Decimal(points) * config.conversion_rate

        if amount > config.max_conversion_limit:
            raise ValidationError(f"Cannot convert more than ${config.max_conversion_limit} at once.")

        with transaction.atomic():
            # Deduct points (loyalty side)
            LoyaltyConversionService.deduct_points(
                client_profile=client,
                points=points,
                website=website,
                reason="Converted to wallet balance"
            )

            # Credit wallet (wallet side)
            WalletTransactionService.credit(
                user=client.user,
                website=website,
                amount=amount,
                transaction_type="loyalty_point",  # optional override
                source="loyalty_conversion",
                description="Loyalty Points Conversion",
                note=f"Converted {points} points"
            )

        return amount
    

    @staticmethod
    def try_auto_convert(client_profile, website):
        config = LoyaltyPointsConversionConfig.objects.filter(website=website, active=True).first()
        if not config:
            return

        points = client_profile.loyalty_points
        if points < config.min_conversion_points:
            return

        # Round down to nearest convertible block
        convertible_points = (points // config.min_conversion_points) * config.min_conversion_points

        if convertible_points:
            LoyaltyConversionService.convert_points_to_wallet(
                client=client_profile,
                website=website,
                points=convertible_points
            )

            # Notify user
            from notifications_system.utils import send_user_notification
            send_user_notification(
                user=client_profile.user,
                title="Loyalty Points Converted",
                message=f"{convertible_points} loyalty points were converted to wallet balance.",
                type="wallet_credit"
            )

    @staticmethod
    def sync_loyalty_cache(client_profile):
        total = LoyaltyConversionService.get_total_points(client_profile)
        if client_profile.loyalty_points != total:
            client_profile.loyalty_points = total
            client_profile.save()

        return total
