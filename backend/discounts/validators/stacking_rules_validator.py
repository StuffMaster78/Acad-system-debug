"""
Validator for discount stacking rules.
"""

from rest_framework.exceptions import ValidationError
from discounts.utils import get_discount_usage_model


class StackingRulesValidator:
    """
    Validates whether discounts can be stacked for a given user/order context.
    """

    def __init__(self, user):
        self.user = user
        self.usage_model = get_discount_usage_model()

    def is_stackable(self, discount):
        """
        Check if a discount is generally stackable.

        Args:
            discount (Discount): Discount to check.

        Returns:
            bool: True if stackable, False otherwise.
        """
        return discount.stackable

    def validate_stackable_usage_limit(self, discount):
        """
        Validate stackable usage limit for the user.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If max stackable usage exceeded.
        """
        if discount.max_stackable_uses_per_customer is None:
            return

        count = self.usage_model.objects.filter(
            user=self.user, discount=discount
        ).count()

        if count >= discount.max_stackable_uses_per_customer:
            raise ValidationError(
                f"Discount {discount.code} stackable usage exceeded "
                f"({discount.max_stackable_uses_per_customer} max)."
            )

    def check_mutual_compatibility(self, discounts):
        """
        Validate that all discounts in a list are compatible with each other.

        Args:
            discounts (list[Discount]): List of discounts to validate.

        Raises:
            ValidationError: If any combination is incompatible.
        """
        for d1 in discounts:
            for d2 in discounts:
                if d1 == d2:
                    continue
                if not d1.stackable_with.filter(id=d2.id).exists():
                    raise ValidationError(
                        f"Discounts {d1.code} and {d2.code} cannot be stacked."
                    )