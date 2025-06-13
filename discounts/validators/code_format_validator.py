"""
Validates the format of discount codes.
"""

import re
from django.core.exceptions import ValidationError


class CodeFormatValidator:
    """
    Validates the format of a discount code.

    Enforces uppercase alphanumeric characters and optionally hyphens,
    with a length between 5 and 20 characters.
    """

    CODE_REGEX = re.compile(r"^[A-Z0-9\-]{5,20}$")

    def is_valid_format(self, code):
        """
        Validate the given discount code.

        Args:
            code (str): The discount code to validate.

        Raises:
            ValidationError: If the code format is invalid.
        """
        if not isinstance(code, str):
            raise ValidationError("Discount code must be a string.")

        if not self.CODE_REGEX.match(code):
            raise ValidationError(
                "Invalid discount code format. Code must be 5-20 characters, "
                "uppercase letters, numbers, or hyphens only."
            )