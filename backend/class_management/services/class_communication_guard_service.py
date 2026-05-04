from __future__ import annotations

import re
from typing import Any

from django.core.exceptions import ValidationError

EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")


class ClassCommunicationGuardService:
    """
    Guardrails for class communication.

    Prevents off-platform contact sharing and unsafe content.
    """

    @staticmethod
    def validate_message_body(*, body: str) -> None:
        """
        Block emails and phone numbers in messages.
        """
        if EMAIL_PATTERN.search(body):
            raise ValidationError(
                "Email addresses are not allowed in class messages."
            )

        if PHONE_PATTERN.search(body):
            raise ValidationError(
                "Phone numbers are not allowed in class messages."
            )

    @staticmethod
    def validate_sender_can_message(
        *,
        class_order,
        sender,
    ) -> None:
        """
        Ensure sender is allowed to participate in this class thread.
        """
        if getattr(sender, "is_staff", False) or getattr(
            sender, "is_superuser", False
        ):
            return

        if getattr(class_order, "client_id", None) == getattr(
            sender, "id", None
        ):
            return

        assigned_writer_id = getattr(
            class_order,
            "assigned_writer_id",
            None,
        )

        if assigned_writer_id == getattr(sender, "id", None):
            return

        raise ValidationError(
            "You cannot send messages for this class."
        )