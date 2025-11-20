"""
Validator for checking discount applicability based on order context.
"""

from django.utils.timezone import now
from rest_framework.exceptions import ValidationError


class OrderDiscountValidator:
    """
    Validates whether a discount is applicable to a given order.
    """

    def __init__(self, order):
        self.order = order
        self.user = order.user

    def validate_order_value(self, discount):
        """
        Validate if the order meets the minimum value for the discount.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If order value is too low.
        """
        if discount.min_order_value and self.order.total < discount.min_order_value:
            raise ValidationError(
                f"Order total must be at least {discount.min_order_value} "
                f"to use discount {discount.code}."
            )

    def validate_first_order_only(self, discount):
        """
        Validate if the discount is for first-time buyers only.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If user has previous orders.
        """
        if discount.applies_to_first_order_only and self.user.orders.exists():
            raise ValidationError(
                f"Discount {discount.code} is only for first-time customers."
            )

    def validate_active_period(self, discount):
        """
        Validate if the discount is currently active.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If discount is not active or expired.
        """
        now_time = now()

        if not discount.is_active:
            raise ValidationError(
                f"Discount {discount.code} is inactive."
            )

        if discount.valid_from and discount.valid_from > now_time:
            raise ValidationError(
                f"Discount {discount.code} is not yet valid."
            )

        if discount.valid_until and discount.valid_until < now_time:
            raise ValidationError(
                f"Discount {discount.code} has expired."
            )