"""
Validates discount usage limits per user and global max uses.
"""

from django.core.exceptions import ValidationError
from discounts.utils import get_discount_usage_model


class DiscountUsageValidator:
    """
    Validates discount usage counts for global and per-user limits.
    """

    @classmethod
    def validate_per_user_limit(cls, discount, user):
        """
        Check if a user has exceeded the max usage allowed for a discount.

        Args:
            discount (Discount): Discount instance to check.
            user (User): User instance to validate usage for.

        Raises:
            ValidationError: If user has reached max usage limit.
        """
        usage_model = get_discount_usage_model()
        used_count = usage_model.objects.filter(
            user=user,
            discount=discount
        ).count()

        if discount.max_uses_per_user and used_count >= discount.max_uses_per_user:
            raise ValidationError(
                f"Discount '{discount.code}' can only be used "
                f"{discount.max_uses_per_user} times per user."
            )
        
    @classmethod
    def validate_global_limit(cls, discount):
        """
        Check if a discount has reached its global max usage limit.

        Args:
            discount (Discount): Discount instance to check.

        Raises:
            ValidationError: If discount usage limit has been reached.
        """
        if discount.max_uses and discount.used_count >= discount.max_uses:
            raise ValidationError(
                f"Discount '{discount.code}' has reached its usage limit, contact support."
            )