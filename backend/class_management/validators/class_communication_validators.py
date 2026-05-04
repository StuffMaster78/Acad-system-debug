from __future__ import annotations

import re

from django.core.exceptions import ValidationError


EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")


class ClassCommunicationValidator:
    """
    Prevent off-platform contact sharing.
    """

    @staticmethod
    def validate_message_body(*, body: str) -> None:
        if EMAIL_PATTERN.search(body):
            raise ValidationError(
                "Email addresses are not allowed in class messages."
            )

        if PHONE_PATTERN.search(body):
            raise ValidationError(
                "Phone numbers are not allowed in class messages."
            )