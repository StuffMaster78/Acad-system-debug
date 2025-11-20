"""
Validator for checking user-based discount eligibility.
"""

from rest_framework.exceptions import ValidationError
from discounts.utils import get_discount_usage_model


class UserEligibilityValidator:
    """
    Validates if a user is eligible to apply a given discount.
    """

    def __init__(self, user):
        self.user = user
        self.usage_model = get_discount_usage_model()

    def validate_per_user_limit(self, discount):
        """
        Validate that the user has not exceeded their per-user usage limit.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If user exceeded allowed usage.
        """
        if discount.per_user_limit is not None:
            count = self.usage_model.objects.filter(
                user=self.user, discount=discount
            ).count()
            if count >= discount.per_user_limit:
                raise ValidationError(
                    f"You've already used discount {discount.code} "
                    f"{discount.per_user_limit} times."
                )

    def validate_max_stackable_uses(self, discount):
        """
        Validate user's usage against max stackable uses.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If stackable use limit is exceeded.
        """
        if discount.max_stackable_uses_per_customer is not None:
            count = self.usage_model.objects.filter(
                user=self.user, discount=discount
            ).count()
            if count >= discount.max_stackable_uses_per_customer:
                raise ValidationError(
                    f"You've already used discount {discount.code} "
                    f"{discount.max_stackable_uses_per_customer} times."
                )