"""
Tracks and reverts discount usage records tied to orders.
"""

import logging
from django.db.models import F
from audit_logging.services.audit_log_service import AuditLogService

logger = logging.getLogger(__name__)


class DiscountUsageTracker:
    """
    Handles creation, incrementing, and deletion of discount usage records.
    """
    def __init__(self):
        """
        Initialize the tracker service.
        """
        pass

    @classmethod
    def track_multiple(cls, discounts, order, user):
        """
        Track usage of multiple discounts for a specific order and user.

        Args:
            discounts (list): List of Discount instances.
            order (Order): The order to which the discounts apply.
            user (User): The user using the discounts.
        """
        for discount in discounts:
            cls.track_single(discount=discount, order=order, user=user)

    @classmethod
    def track_single(cls, discount, order, user=None):
        """
        Track usage of a single discount.

        Args:
            discount (Discount): The discount being used.
            order (Order): The order where the discount is applied.
            user (User, optional): The user using the discount. Defaults to
                order.user.
        """
        from discounts.models import Discount, DiscountUsage
        user = user or order.user
        DiscountUsage.objects.create(
            base_discount=discount,
            user=user,
            website=order.website,
            order=order
        )
        Discount.objects.filter(id=discount.id).update(
            used_count=F("used_count") + 1
        )
        logger.info(
            f"Tracked usage of discount {discount.code} for user {user.id} "
            f"and order {order.id}"
        )

    @classmethod
    def revert(cls, order):
        """
        Revert all discount usage records for a given order.

        This does not update the used_count of the discount.

        Args:
            order (Order): The order whose discount usages are to be reverted.
        """
        from discounts.models import DiscountUsage
        deleted_count, _ = DiscountUsage.objects.filter(order=order).delete()
        logger.info(
            f"Reverted {deleted_count} discount usages for order {order.id}"
        )

    @classmethod
    def untrack(cls, order, discount=None, actor=None, reason=None):
        """
        Revert and decrement usage of one or all discounts for an order.

        Args:
            order (Order): The order to untrack discounts for.
            discount (Discount, optional): If provided, untracks only this
                discount. If None, untracks all.
            actor (User, optional): The actor triggering the untrack. Used for
                audit logging.
            reason (str, optional): Reason for untracking. Logged for context.
        """
        from discounts.models import Discount, DiscountUsage
        usages = DiscountUsage.objects.filter(order=order)
        if discount:
            usages = usages.filter(base_discount=discount)

        if not usages.exists():
            logger.info(
                f"No discount usages found to untrack for order {order.id}"
            )
            return

        codes = list(
            usages.values_list("base_discount__code", flat=True)
        )

        for usage in usages:
            Discount.objects.filter(id=usage.base_discount_id).update(
                used_count=F("used_count") - 1
            )

        count = usages.count()
        usages.delete()

        logger.info(
            f"Untracked {count} discount usages for order {order.id}. "
            f"Reason: {reason}"
        )

        AuditLogService.log(
            actor=actor,
            target=order,
            action="discount_untracked",
            metadata={
                "discount_codes": codes,
                "reason": reason,
            }
        )

    @classmethod
    def has_user_used(cls, discount, user):
        """
        Check if a user has previously used a discount.

        Args:
            discount (Discount): The discount to check.
            user (User): The user to check for.

        Returns:
            bool: True if used, False otherwise.
        """
        from discounts.models import DiscountUsage
        return DiscountUsage.objects.filter(
            base_discount=discount,
            user=user
        ).exists()

    @classmethod
    def get_usage_count(cls, discount):
        """
        Get total number of times a discount has been used.

        Args:
            discount (Discount): The discount to count usages for.

        Returns:
            int: Usage count.
        """
        from discounts.models import DiscountUsage
        return DiscountUsage.objects.filter(
            base_discount=discount
        ).count()