from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from class_management.validators.class_communication_validators import (
    ClassCommunicationValidator,
)


def test_message_rejects_email():
    with pytest.raises(ValidationError):
        ClassCommunicationValidator.validate_message_body(
            body="Email me at test@example.com",
        )


def test_message_rejects_phone():
    with pytest.raises(ValidationError):
        ClassCommunicationValidator.validate_message_body(
            body="WhatsApp me on +254712345678",
        )


def test_message_allows_normal_text():
    ClassCommunicationValidator.validate_message_body(
        body="Please upload the draft through the system.",
    )