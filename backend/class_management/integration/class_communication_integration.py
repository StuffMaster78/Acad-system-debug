from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework.exceptions import ValidationError

from class_management.models.class_order import ClassOrder
from class_management.services.class_communication_guard_service import (
    ClassCommunicationGuardService,
)


class ClassCommunicationIntegrationService:
    """
    Bridge class orders to the central communications app.

    The communications app owns threads, messages, read receipts, flags,
    reactions, and message notifications.
    """

    THREAD_TYPE = "class_order"

    @classmethod
    @transaction.atomic
    def get_or_create_thread(
        cls,
        *,
        class_order: ClassOrder,
        created_by=None,
    ):
        """
        Return the class order communication thread.
        """
        from communications.models import CommunicationThread

        content_type = ContentType.objects.get_for_model(ClassOrder)

        thread, _ = CommunicationThread.objects.get_or_create(
            website=class_order.website,
            thread_type=cls.THREAD_TYPE,
            content_type=content_type,
            object_id=class_order.pk,
            defaults={
                "subject": cls._build_subject(class_order=class_order),
                "is_active": True,
                "allow_messaging": True,
            },
        )

        thread.participants.add(class_order.client)

        assigned_writer = cls._get_related_obj(
            obj=class_order,
            field_name="assigned_writer",
        )

        if assigned_writer is not None:
            thread.participants.add(assigned_writer)

        if created_by is not None:
            thread.participants.add(created_by)

        return thread

    @classmethod
    @transaction.atomic
    def send_message(
        cls,
        *,
        class_order: ClassOrder,
        sender,
        recipient,
        body: str,
        message_type: str = "text",
        is_internal_note: bool = False,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Send a class-linked communication message.
        """
        from communications.models import CommunicationMessage

        ClassCommunicationGuardService.validate_sender_can_message(
            class_order=class_order,
            sender=sender,
        )
        ClassCommunicationGuardService.validate_message_body(body=body)

        thread = cls.get_or_create_thread(
            class_order=class_order,
            created_by=sender,
        )

        cls._ensure_thread_can_message(thread=thread)

        thread.participants.add(sender, recipient)

        return CommunicationMessage.objects.create(
            thread=thread,
            sender=sender,
            recipient=recipient,
            message=body,
            message_type=message_type,
            is_internal_note=is_internal_note,
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def post_system_update(
        cls,
        *,
        class_order: ClassOrder,
        body: str,
        recipient=None,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Post a system-generated update to the class thread.
        """
        recipient = recipient or class_order.client
        sender = triggered_by or recipient

        return cls.send_message(
            class_order=class_order,
            sender=sender,
            recipient=recipient,
            body=body,
            message_type="system",
            metadata={
                "source": "class_management",
                **(metadata or {}),
            },
        )

    @classmethod
    def list_messages(cls, *, class_order: ClassOrder):
        """
        Return visible messages for the class order thread.
        """
        from communications.models import CommunicationMessage

        thread = cls.get_or_create_thread(class_order=class_order)

        return (
            CommunicationMessage.objects.filter(
                thread=thread,
                is_deleted=False,
                is_hidden=False,
            )
            .select_related("sender", "recipient")
            .order_by("sent_at")
        )

    @staticmethod
    def _build_subject(*, class_order: ClassOrder) -> str:
        """
        Build a stable communication thread subject.
        """
        return f"Class #{class_order.pk}: {class_order.title}"

    @staticmethod
    def _ensure_thread_can_message(*, thread) -> None:
        """
        Block messaging when the communication thread is closed.
        """
        if not thread.is_active or not thread.allow_messaging:
            raise ValidationError(
                "Messaging is disabled for this class."
            )

    @staticmethod
    def _get_related_obj(*, obj: Any, field_name: str) -> Any:
        """
        Return a related object safely.
        """
        return getattr(obj, field_name, None)