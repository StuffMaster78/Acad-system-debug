from __future__ import annotations

from typing import Any

from class_management.services.class_communication_service import (
    ClassCommunicationService,
)


class ClassCommunicationIntegrationService:
    """
    Backward-compatible adapter for class communication workflows.

    The current implementation lives in ClassCommunicationService. This
    adapter preserves older import paths while using the centralized
    communications schema.
    """

    @classmethod
    def get_or_create_thread(
        cls,
        *,
        class_order,
        created_by=None,
    ):
        """
        Return the class order communication thread.
        """
        return ClassCommunicationService.get_or_create_thread(
            class_order=class_order,
        )

    @classmethod
    def send_message(
        cls,
        *,
        class_order,
        sender,
        recipient,
        body: str,
        message_type: str = "user",
        is_internal_note: bool = False,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Send a class-linked communication message.
        """
        return ClassCommunicationService.send_message(
            class_order=class_order,
            sender=sender,
            recipient=recipient,
            sender_role=ClassCommunicationService._role_for_user(sender),
            recipient_role=ClassCommunicationService._role_for_user(
                recipient,
            ),
            message=body,
            message_type=message_type,
            is_internal_note=is_internal_note,
            metadata=metadata,
        )

    @classmethod
    def post_system_update(
        cls,
        *,
        class_order,
        body: str,
        recipient=None,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Post a system-generated update to the class thread.
        """
        return ClassCommunicationService.send_system_message(
            class_order=class_order,
            recipient=recipient or class_order.client,
            message=body,
            system_type="class_update",
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @classmethod
    def list_messages(cls, *, class_order):
        """
        Return visible messages for the class order thread.
        """
        return ClassCommunicationService.list_messages(
            class_order=class_order,
        )
