"""
Service for tracking and reverting discount usage tied to orders.
"""

import logging
from django.db.models import F

from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def get_discount_model():
    from discounts.models import Discount
    return Discount

def get_discount_usage_model():
    from discounts.models import DiscountUsage
    return DiscountUsage

class DiscountUsageService:
    @staticmethod
    def get_discount_model():
        from discounts.models import Discount
        return Discount

    @staticmethod
    def get_usage_model():
        from discounts.models import DiscountUsage
        return DiscountUsage
    
    @staticmethod
    def track(cls, discounts, order, user):
        """
        Track usage of multiple discounts for a specific order and user.
        Increments the used_count for each discount.

        Args:
            discounts (list): List of Discount instances
            order (Order): The order the discounts apply to
            user (User): The user using the discounts
        """
        Discount = cls.get_discount_model()
        DiscountUsage = cls.get_usage_model()
        for discount in discounts:
            DiscountUsage.objects.create(
                user=user,
                website=order.website,
                base_discount=discount,
                order=order
            )
            Discount.objects.filter(id=discount.id).update(
                used_count=F("used_count") + 1
            )
            logger.info(
                f"Tracked usage of discount {discount.code} "
                f"for user {user.id} and order {order.id}"
            )

    @staticmethod
    def record_usage(cls, discount, order):
        """
        Record a single discount usage for an order.

        Args:
            discount (Discount): Discount instance used
            order (Order): The order it was used on
        """
        Discount = cls.get_discount_model()
        DiscountUsage = cls.get_usage_model()
        DiscountUsage.objects.create(
            base_discount=discount,
            user=order.user,
            website=order.website,
            order=order
        )
        Discount.objects.filter(id=discount.id).update(
            used_count=F("used_count") + 1
        )
        logger.info(
            f"Recorded usage of discount {discount.code} "
            f"for order {order.id} by user {order.user.id}"
        )

    @staticmethod
    def revert_usage(cls, order):
        """
        Revert all discount usage for a given order (e.g. on refund).
        This version only deletes usage records without updating used_count.

        Args:
            order (Order): Order whose discount usage should be reverted
        """
        DiscountUsage = cls.get_usage_model()
        deleted_count, _ = DiscountUsage.objects.filter(order=order).delete()
        logger.info(f"Reverted {deleted_count} discount usages for order {order.id}")

    @staticmethod
    def untrack(cls, order):
        """
        Revert discount usage and decrement used_count for each discount.
        Useful when an order is refunded or canceled.

        Args:
            order (Order): The order to untrack discounts for
        """
        Discount = cls.get_discount_model()
        DiscountUsage = cls.get_usage_model()
        
        usages = DiscountUsage.objects.filter(order=order)
        if not usages.exists():
            logger.info(f"No discount usages found to untrack for order {order.id}")
            return

        for usage in usages:
            Discount.objects.filter(id=usage.base_discount_id).update(
                used_count=F("used_count") - 1
            )
        count = usages.count()
        usages.delete()

        logger.info(f"Untracked {count} discounts for order {order.id}")

    @classmethod
    def check_usage_per_user_limit(cls, discount, user):
        """
        Validate if the user has exceeded per-user usage limit.
        """
        DiscountUsage = cls.get_usage_model()
        count = DiscountUsage.objects.filter(
            user=user,
            base_discount=discount
        ).count()
        if discount.max_uses_per_user and count >= discount.max_uses_per_user:
            raise ValidationError(
                f"Discount can only be used {discount.max_uses_per_user} times."
            )
    @classmethod
    def increment_usage(cls, discount):
        """
        Increment used_count if under global usage limit.
        """
        Discount = cls.get_discount_model()
        if discount.max_uses and discount.used_count >= discount.max_uses:
            raise ValidationError("Discount usage limit reached.")

        Discount.objects.filter(id=discount.id).update(
            used_count=F("used_count") + 1
        )


    def finalize_discount_usage(self):
        """ Finalizes all the discount usage records in the system """
        # Assumes `apply_discounts` was already run
        pass