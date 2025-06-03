"""
Validator for checking discount stacking rules.
"""

from rest_framework.exceptions import ValidationError
from discounts.utils import get_discount_usage_model


class DiscountStackingValidator:
    """
    Validates whether a discount can be stacked with others for a given user.
    """

    def __init__(self, user):
        self.user = user
        self.usage_model = get_discount_usage_model()

    def validate_stackable_flag(self, discount):
        """
        Validate the basic stackable flag.

        Args:
            discount (Discount): The discount to check.

        Raises:
            ValidationError: If the discount isn't stackable.
        """
        if not discount.stackable:
            raise ValidationError(
                f"Discount {discount.code} is not stackable."
            )

    def validate_max_stackable_uses(self, discount):
        """
        Validate how many times a user can stack this discount.

        Args:
            discount (Discount): The discount to check.

        Raises:
            ValidationError: If the user exceeded stackable usage limit.
        """
        if discount.max_stackable_uses_per_customer is None:
            return

        count = self.usage_model.objects.filter(
            user=self.user, discount=discount
        ).count()

        if count >= discount.max_stackable_uses_per_customer:
            raise ValidationError(
                f"You've already used {discount.code} "
                f"{count} times, which exceeds the stackable usage limit."
            )

    def validate_stacking_compatibility(self, discount, applied_discounts):
        """
        Validates whether a discount can be stacked with others.

        Args:
            discount (Discount): The discount to test.
            applied_discounts (list): List of discounts already applied.

        Raises:
            ValidationError: If stacking rules are violated.
        """
        incompatible = [
            d for d in applied_discounts
            if not discount.stackable_with.filter(id=d.id).exists()
        ]
        if incompatible:
            raise ValidationError(
                f"Discount {discount.code} can't be stacked with "
                f"{', '.join([d.code for d in incompatible])}."
            )