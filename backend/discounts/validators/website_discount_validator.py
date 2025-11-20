"""
Validator for checking if a discount is valid for a specific website.
"""

from rest_framework.exceptions import ValidationError


class WebsiteDiscountValidator:
    """
    Validates whether a discount is allowed for the current website.
    """

    def __init__(self, website):
        self.website = website

    def validate_website_match(self, discount):
        """
        Validate if the discount belongs to the provided website.

        Args:
            discount (Discount): Discount to validate.

        Raises:
            ValidationError: If website mismatch occurs.
        """
        if discount.website != self.website:
            raise ValidationError(
                f"Discount {discount.code} is not valid on this website."
            )