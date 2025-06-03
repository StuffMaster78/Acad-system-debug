"""
Validator for checking order-based discount eligibility.
"""

from django.utils.timezone import now
from rest_framework.exceptions import ValidationError


class OrderEligibilityValidator:
    """
    Validates if an order is eligible for a given discount.
    """

    def __init__(self, order, current_time=None):
        self.order = order
        self.current_time = current_time or now()

    def validate_order_minimum(self, discount):
        """
        Validate that the order total meets the discount's minimum value.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If the order total is below the minimum.
        """
        if discount.min_order_value is not None:
            if self.order.total < discount.min_order_value:
                raise ValidationError(
                    f"Order must be at least ${discount.min_order_value} "
                    f"to use discount {discount.code}."
                )

    def validate_first_order_only(self, discount):
        """
        Validate that the discount is for first-time orders only.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If user is not a first-time buyer.
        """
        if discount.applies_to_first_order_only:
            if self.order.user.orders.exists():
                raise ValidationError(
                    f"Discount {discount.code} is only valid for first-time orders."
                )

    def validate_order_window(self, discount):
        """
        Optional: Validate the discount is within the allowed order time window.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If the order does not fall within the window.
        """
        if discount.start_date and discount.start_date > self.current_time:
            raise ValidationError(
                f"Discount {discount.code} is not active yet."
            )
        if discount.end_date and discount.end_date < self.current_time:
            raise ValidationError(
                f"Discount {discount.code} has expired."
            )