"""Handles validation of discount code input format."""

import re
import logging
from django.core.exceptions import ValidationError
from discounts.models import Discount  # or `get_discount_model()` if dynamic
# from discounts.services.discount_config import DiscountConfig  # if needed

logger = logging.getLogger(__name__)


class DiscountCodeValidator:
    """Validates single or multiple discount code inputs."""

    def __init__(self, codes):
        """
        Initialize the DiscountCodeValidator.

        Args:
            codes (str or list): A single discount code or list of codes.
        """
        if isinstance(codes, str):
            self.codes = [codes.strip()]
        elif isinstance(codes, list):
            self.codes = [code.strip() for code in codes]
        else:
            raise TypeError("Codes must be a string or list of strings.")

    def validate(self):
        """Run basic format validations on all codes."""
        for code in self.codes:
            if not self._is_valid_format(code):
                raise ValidationError(f"Invalid discount code format: {code}")

    @staticmethod
    def _is_valid_format(code):
        """
        Check if the code matches a basic alphanumeric pattern.

        Args:
            code (str): The discount code to validate.

        Returns:
            bool: True if format is valid, False otherwise.
        """
        return bool(re.match(r'^[A-Z0-9_-]{4,30}$', code, re.IGNORECASE))

    @staticmethod
    def is_valid_code(code):
        """
        Check discount code length boundaries.

        Args:
            code (str): The discount code to validate.

        Returns:
            bool: True if valid length, False otherwise.
        """
        return 3 <= len(code) <= 20 if code else False

    @staticmethod
    def validate_discount_code(code, website):
        """
        Validate a single discount code against the database.

        Args:
            code (str): The discount code to validate.
            website (Website): The website where the discount applies.

        Returns:
            Discount: The validated discount object.

        Raises:
            ValidationError: If the code is invalid or inactive.
        """
        if not DiscountCodeValidator._is_valid_format(code):
            raise ValidationError("Invalid discount code format.")

        try:
            return Discount.objects.get(
                code=code, website=website, is_active=True
            )
        except Discount.DoesNotExist:
            raise ValidationError("Discount code not found or inactive.")

    @staticmethod
    def validate_discount_codes(codes, website):
        """
        Validate multiple discount codes against the database.

        Args:
            codes (list): List of discount codes.
            website (Website): The website where the discounts apply.

        Returns:
            list: List of validated Discount objects.

        Raises:
            ValidationError: If no valid discount codes are found.
        """
        valid_discounts = []
        for code in codes:
            try:
                discount = DiscountCodeValidator.validate_discount_code(
                    code, website
                )
                valid_discounts.append(discount)
            except ValidationError as e:
                logger.warning(f"Discount code '{code}' failed: {e}")

        if not valid_discounts:
            raise ValidationError("No valid discount codes found.")

        return valid_discounts