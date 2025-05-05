import random
import string
from django.utils import timezone
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from discounts.models import Discount, DiscountUsage, SeasonalEvent
from discounts.validators import DiscountValidator
from django.db.models import F
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from notifications_system.services.send_notification import (
    notify_admin_of_error
)
from users.models import User
from orders.models import Order
from .discounts import DiscountService
import logging


class DiscountStackingService:
    """
    Service for handling discount stacking rules.
    Ensures discounts are applied according to stackability rules.
    """

    @staticmethod
    def can_stack(discount, other_discount):
        """
        Check if two discounts can be stacked based on rules.
        For example: 'WELCOME10' may not stack with 'SUMMER20'.
        """
        if discount.stackable and other_discount.stackable:
            if other_discount in discount.stackable_with.all():
                return True
        return False

    @staticmethod
    def get_stackable_discounts(discount):
        """
        Return a list of discounts that can be stacked with the given discount.
        """
        return discount.stackable_with.all()

    @staticmethod
    def check_discount_stacking_for_order(order, discounts):
        """
        Checks if multiple discounts can be stacked on an order.
        Returns the discounts that can be applied and those that cannot.
        """
        applicable_discounts = []
        non_applicable_discounts = []

        for i, discount in enumerate(discounts):
            for j in range(i+1, len(discounts)):
                if not DiscountStackingService.can_stack(discount, discounts[j]):
                    non_applicable_discounts.append(discounts[j])
                    continue
            applicable_discounts.append(discount)

        return applicable_discounts, non_applicable_discounts

    @staticmethod
    def apply_stacked_discounts(order, discounts):
        """
        Applies the stackable discounts to the order.
        Ensures that all discounts can be applied together.
        """
        applicable_discounts, non_applicable = DiscountStackingService.check_discount_stacking_for_order(order, discounts)

        if len(applicable_discounts) == 0:
            raise ValidationError("No valid discounts available for stacking.")

        final_price = order.total_price
        applied_discounts = []

        for discount in applicable_discounts:
            # Apply the discount logic (percentage/fixed/etc.)
            applied_discount_value = DiscountService(discount).apply_discount(final_price)
            final_price -= applied_discount_value
            applied_discounts.append({
                "discount": discount.code,
                "applied_amount": applied_discount_value,
            })

        return final_price, applied_discounts