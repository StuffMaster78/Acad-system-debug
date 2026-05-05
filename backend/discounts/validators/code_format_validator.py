from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class DiscountCodeFormatValidator:
    """
    Validate discount code format.

    Codes should be uppercase and may contain letters, numbers, and
    hyphens only.
    """

    pattern = re.compile(r"^[A-Z0-9-]+$")

    def __call__(self, value: str) -> None:
        """
        Validate the given discount code.
        """
        if not value:
            raise ValidationError("Discount code is required.")

        if value != value.upper():
            raise ValidationError(
                "Discount code must use uppercase characters."
            )

        if not self.pattern.match(value):
            raise ValidationError(
                "Discount code may only contain uppercase letters, "
                "numbers, and hyphens."
            )

    def __eq__(self, other) -> bool:
        """
        Support Django migration serialization comparisons.
        """
        return isinstance(other, DiscountCodeFormatValidator)