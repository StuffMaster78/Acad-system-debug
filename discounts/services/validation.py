"""
Validates discount codes before use.
"""

from django.utils.timezone import now
from rest_framework.exceptions import ValidationError


class DiscountValidationService:
    """
    Service for validating discount codes before applying them to an order.
    """

    @staticmethod
    def validate_discounts(discounts, website, order):
        """
        Validates a list of discounts before applying.

        Args:
            discounts: List of Discount instances
            website: Website instance
            order: Order instance

        Raises:
            ValidationError if any code is invalid.
        """
        current_time = now()
        for discount in discounts:
            DiscountValidationService._validate_discount(
                discount, website,
                current_time
            )
            
    @staticmethod
    def _validate_discount(discount, website, current_time):
        """
        Validates a single discount code.

        Args:
            discount: Discount instance to validate
            website: Website instance to check against
            current_time: The current time to check validity

        Raises:
            ValidationError if the discount code is invalid.
        """
        if discount.website != website:
            raise ValidationError(
                f"Discount {discount.code} is not valid on this website."
                )
        if not discount.is_active:
            raise ValidationError(
                f"Discount {discount.code} is inactive."
            )
        if discount.valid_from > current_time:
            raise ValidationError(
                f"Discount {discount.code} is not yet valid."
            )
        if discount.valid_until < current_time:
            raise ValidationError(
                f"Discount {discount.code} has expired."
            )
        if discount.usage_limit is not None:
            if discount.used_count >= discount.usage_limit:
                raise ValidationError(
                    f"Discount {discount.code} has reached its usage limit."
                    )