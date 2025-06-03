"""Handles core business validations for discount usage."""

from datetime import date
from discounts.models import DiscountUsage


class DiscountValidator:
    """Performs core discount validation logic."""

    def __init__(self, discount, user=None, order_total=None, codes=None):
        """
        Initialize the DiscountValidator.

        Args:
            discount (Discount): The discount object to validate.
            user (User, optional): The user attempting to use the discount.
            order_total (Decimal, optional): Total value of the order.
        """
        self.discount = discount
        self.user = user
        self.order_total = order_total
        self.codes = codes
    def validate(self):
        """Run all core validations."""
        self._check_date_validity()
        self._check_usage_limits()
        self._check_min_order_value()

    def _check_date_validity(self):
        """Ensure the discount is currently valid."""
        today = date.today()
        if self.discount.start_date and self.discount.start_date > today:
            raise ValueError("Discount not yet valid.")
        if self.discount.end_date and self.discount.end_date < today:
            raise ValueError("Discount has expired.")

    def _check_usage_limits(self):
        """Ensure the user hasn't exceeded usage limits."""
        if self.user and self.discount.per_user_limit:
            usage_count = DiscountUsage.objects.filter(
                discount=self.discount,
                user=self.user
            ).count()
            if usage_count >= self.discount.per_user_limit:
                raise ValueError("Usage limit for this discount exceeded.")

    def _check_min_order_value(self):
        """Ensure the order meets the minimum total required."""
        if self.discount.min_order_value and self.order_total is not None:
            if self.order_total < self.discount.min_order_value:
                raise ValueError("Order value too low for this discount.")