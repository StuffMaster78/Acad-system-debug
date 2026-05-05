from __future__ import annotations

from django.core.exceptions import ValidationError

from communications.constants import CommunicationMessageStatus


class CommunicationMessageValidator:
    """
    Validators for communication messages.
    """

    @staticmethod
    def validate_body(*, body: str) -> None:
        """
        Validate message body.
        """
        if not body or not body.strip():
            raise ValidationError("Message body cannot be empty.")

    @staticmethod
    def validate_can_edit(*, message) -> None:
        """
        Validate message can be edited.
        """
        if message.status != CommunicationMessageStatus.ACTIVE:
            raise ValidationError("Only active messages can be edited.")

        if message.is_system_generated:
            raise ValidationError("System messages cannot be edited.")

    @staticmethod
    def validate_can_hide(*, message) -> None:
        """
        Validate message can be hidden.
        """
        if message.status in {
            CommunicationMessageStatus.WITHDRAWN,
            CommunicationMessageStatus.DELETED,
        }:
            raise ValidationError("This message cannot be hidden.")

    @staticmethod
    def validate_can_withdraw(*, message) -> None:
        """
        Validate message can be withdrawn.
        """
        if message.status in {
            CommunicationMessageStatus.WITHDRAWN,
            CommunicationMessageStatus.DELETED,
        }:
            raise ValidationError("This message cannot be withdrawn.")