"""
Service for determining and applying valid stackable discounts to orders.
"""

import logging
from decimal import Decimal
from itertools import combinations

from django.apps import apps
from django.core.exceptions import ValidationError

from .config import DiscountConfigService

logger = logging.getLogger(__name__)


def get_discount_model():
    """
    Dynamically retrieves the Discount model from the discounts app.
    """
    return apps.get_model("discounts", "Discount")


class DiscountStackingService:
    """
    Check if two discounts can be stacked together (symmetrical check).
    Args:
        discount1 (Discount): First discount
        discount2 (Discount): Second discount
    Returns:
        bool: True if the discounts can stack together.
    """
    @staticmethod
    def can_stack(discount1, discount2):
        """
        Check if two discounts can stack (symmetrically).
        """
        return (
            discount1.stackable
            and discount2.stackable
            and (
                discount2 in discount1.stackable_with.all()
                or discount1 in discount2.stackable_with.all()
            )
        )

    @staticmethod
    def can_stack_all(discounts):
        """
        Check if all discounts in the list can be mutually stacked.

        Args:
            discounts (list): List of Discount instances

        Returns:
            bool: True if all are mutually stackable.
        """
        for i in range(len(discounts)):
            for j in range(i + 1, len(discounts)):
                if not DiscountStackingService.can_stack(
                    discounts[i], discounts[j]
                ):
                    return False
        return True
    @staticmethod
    def get_stackable_discounts(discount):
        """
        Return all discounts that the given one can stack with.

        Args:
            discount (Discount): The base discount

        Returns:
            QuerySet: Discounts that can stack with this one
        """
        return discount.stackable_with.all()

    @staticmethod
    def check_discount_stacking_for_order(order, discounts):
        """
        Determine the best subset of stackable discounts for an order.

        Args:
            order (Order): The order to apply the discounts to
            discounts (list): List of Discount instances

        Returns:
            tuple:
                - list of applicable stackable discounts
                - list of discounts that were excluded
        """
        website = order.website  # assumes order has a `website` FK
        config = DiscountConfigService.get_config(website)
        max_stack = config.get("MAX_STACKABLE_DISCOUNTS", 1)
        enable_stacking = config.get("ENABLE_STACKING", True)

        if not enable_stacking:
            # Pick the single best discount if stacking is off
            best = max(discounts, key=lambda d: d.value, default=None)
            if best:
                ignored = [d for d in discounts if d != best]
                return [best], ignored
            return [], discounts

        best_stack = []
        best_value = Decimal("0.00")
        max_r = min(max_stack, len(discounts))

        for r in range(1, max_r + 1):
            for subset in combinations(discounts, r):
                if DiscountStackingService.can_stack_all(subset):
                    total = sum([d.value for d in subset])
                    if total > best_value:
                        best_stack = list(subset)
                        best_value = total

        ignored = [d for d in discounts if d not in best_stack]
        return best_stack, ignored