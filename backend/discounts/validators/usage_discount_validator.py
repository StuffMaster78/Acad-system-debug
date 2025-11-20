"""
Validator for enforcing discount usage limits.
"""

from rest_framework.exceptions import ValidationError
from django.utils.timezone import now


class UsageDiscountValidator:
    """
    Validates discount usage limits, date ranges, and active status.
    """

    def __init__(self, current_time=None):
        self.current_time = current_time or now()

    def validate_usage_limit(self, discount):
        """
        Validate that the discount has not exceeded its usage limit.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If usage limit is exceeded.
        """
        if discount.usage_limit is not None:
            if discount.used_count >= discount.usage_limit:
                raise ValidationError(
                    f"Discount {discount.code} has reached its usage limit."
                )

    def validate_date_range(self, discount):
        """
        Validate if the current time is within the discount's validity period.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If the discount is not yet valid or expired.
        """
        if discount.valid_from and discount.valid_from > self.current_time:
            raise ValidationError(
                f"Discount {discount.code} is not yet valid."
            )

        if discount.valid_until and discount.valid_until < self.current_time:
            raise ValidationError(
                f"Discount {discount.code} has expired."
            )

    def validate_is_active(self, discount):
        """
        Validate that the discount is active.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If the discount is inactive.
        """
        if not discount.is_active:
            raise ValidationError(
                f"Discount {discount.code} is inactive."
            )