"""
Validator for checking if a discount is within its valid date range.
"""

from django.utils.timezone import now
from rest_framework.exceptions import ValidationError


class DiscountDateValidator:
    """
    Validates whether the current time is within the discount's active period.
    """

    @staticmethod
    def validate(discount, current_time=None):
        """
        Validate the discount's date range.

        Args:
            discount (Discount): Discount instance to validate.
            current_time (datetime, optional): Current time override.

        Raises:
            ValidationError: If discount is not active based on dates.
        """
        current_time = current_time or now()

        if discount.start_date and discount.start_date > current_time:
            raise ValidationError("Discount is not active yet.")

        if discount.end_date and discount.end_date < current_time:
            raise ValidationError("Discount has expired.")