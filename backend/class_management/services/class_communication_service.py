from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from communications.models import (
    CommRole,
    CommunicationMessage,
    CommunicationThread,
    MessageType,
)
from class_management.models.class_order import ClassOrder
from class_management.services.class_communication_guard_service import (
    ClassCommunicationGuardService,
)


class ClassCommunicationService:
    """
    Bridge class orders to the existing communications app.

    The communications app owns threads, messages, read receipts,
    flagging, reactions, and notifications. This service only creates
    and retrieves class-linked communication records.
    """

    THREAD_TYPE = "class_order"

    @classmethod
    @transaction.atomic
    def get_or_create_thread(
        cls,
        *,
        class_order: ClassOrder,
        sender_role: str = CommRole.CLIENT,
        recipient_role: str = CommRole.WRITER,
    ) -> CommunicationThread:
        """
        Return the class order thread, creating it when missing.
        """
        content_type = ContentType.objects.get_for_model(ClassOrder)

        thread, created = CommunicationThread.objects.get_or_create(
            website=class_order.website,
            thread_type=cls.THREAD_TYPE,
            content_type=content_type,
            object_id=class_order.pk,
            defaults={
                "subject": cls._build_subject(class_order=class_order),
                "sender_role": sender_role,
                "recipient_role": recipient_role,
                "is_active": True,
                "allow_messaging": True,
            },
        )

        if created:
            cls._add_default_participants(
                thread=thread,
                class_order=class_order,
            )

        return thread

    @classmethod
    @transaction.atomic
    def sync_participants(
        cls,
        *,
        class_order: ClassOrder,
    ) -> CommunicationThread:
        """
        Ensure client and assigned writer are thread participants.
        """
        thread = cls.get_or_create_thread(class_order=class_order)

        cls._add_default_participants(
            thread=thread,
            class_order=class_order,
        )

        return thread

    @classmethod
    @transaction.atomic
    def send_message(
        cls,
        *,
        class_order: ClassOrder,
        sender,
        recipient,
        sender_role: str,
        recipient_role: str,
        message: str,
        message_type: str = MessageType.TEXT,
        is_internal_note: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> CommunicationMessage:
        """
        Send a message inside the class order thread.

        Attachments should be handled by files_management, not here.
        """
        ClassCommunicationGuardService.validate_sender_can_message(
            class_order=class_order,
            sender=sender,
        )
        ClassCommunicationGuardService.validate_message_body(body=message)

        thread = cls.get_or_create_thread(
            class_order=class_order,
            sender_role=sender_role,
            recipient_role=recipient_role,
        )

        cls._ensure_messaging_allowed(thread=thread)

        thread.participants.add(sender, recipient)

        created_message = CommunicationMessage.objects.create(
            thread=thread,
            sender=sender,
            recipient=recipient,
            sender_role=sender_role,
            recipient_role=recipient_role,
            message=message,
            message_type=message_type,
            is_internal_note=is_internal_note,
            metadata=metadata or {},
            is_system=message_type == MessageType.SYSTEM,
        )

        thread.updated_at = created_message.sent_at
        thread.save(update_fields=["updated_at"])

        return created_message

    @classmethod
    @transaction.atomic
    def send_system_message(
        cls,
        *,
        class_order: ClassOrder,
        recipient,
        message: str,
        system_type: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> CommunicationMessage:
        """
        Create a system message for class order events.
        """
        sender = triggered_by or recipient

        return cls.send_message(
            class_order=class_order,
            sender=sender,
            recipient=recipient,
            sender_role=CommRole.ADMIN,
            recipient_role=cls._role_for_user(recipient),
            message=message,
            message_type=MessageType.SYSTEM,
            metadata={
                "system_type": system_type,
                **(metadata or {}),
            },
        )

    @classmethod
    def get_thread(
        cls,
        *,
        class_order: ClassOrder,
    ) -> CommunicationThread | None:
        """
        Return the linked communication thread if it exists.
        """
        content_type = ContentType.objects.get_for_model(ClassOrder)

        return (
            CommunicationThread.objects.filter(
                website=class_order.website,
                thread_type=cls.THREAD_TYPE,
                content_type=content_type,
                object_id=class_order.pk,
            )
            .prefetch_related("participants")
            .first()
        )

    @classmethod
    def list_messages(
        cls,
        *,
        class_order: ClassOrder,
    ):
        """
        Return visible, non-deleted messages for a class order.
        """
        thread = cls.get_thread(class_order=class_order)

        if thread is None:
            return CommunicationMessage.objects.none()

        return (
            CommunicationMessage.objects.filter(
                thread=thread,
                is_deleted=False,
                is_hidden=False,
            )
            .select_related("sender", "recipient")
            .order_by("sent_at")
        )

    @classmethod
    @transaction.atomic
    def disable_thread(
        cls,
        *,
        class_order: ClassOrder,
    ) -> None:
        """
        Disable messaging for a class order thread.
        """
        thread = cls.get_thread(class_order=class_order)

        if thread is None:
            return

        thread.disable_messaging()

    @classmethod
    @transaction.atomic
    def enable_thread(
        cls,
        *,
        class_order: ClassOrder,
    ) -> None:
        """
        Enable messaging through admin override.
        """
        thread = cls.get_thread(class_order=class_order)

        if thread is None:
            cls.get_or_create_thread(class_order=class_order)
            return

        thread.enable_messaging()

    @classmethod
    def _add_default_participants(
        cls,
        *,
        thread: CommunicationThread,
        class_order: ClassOrder,
    ) -> None:
        """
        Add client and assigned writer when available.
        """
        thread.participants.add(class_order.client)

        assigned_writer = cls._get_related_obj(
            obj=class_order,
            field_name="assigned_writer",
        )

        if assigned_writer is not None:
            thread.participants.add(assigned_writer)

    @staticmethod
    def _build_subject(*, class_order: ClassOrder) -> str:
        """
        Build a stable thread subject for a class order.
        """
        return f"Class Order #{class_order.pk}: {class_order.title}"

    @staticmethod
    def _ensure_messaging_allowed(*, thread: CommunicationThread) -> None:
        """
        Block sends when the thread is inactive or locked.
        """
        if not thread.is_active or not thread.allow_messaging:
            raise ValueError("Messaging is disabled for this class order.")

    @staticmethod
    def _role_for_user(user) -> str:
        """
        Best-effort role mapping.

        Replace this with your accounts/users role helper if one exists.
        """
        role = getattr(user, "role", "")

        if role:
            return str(role)

        if getattr(user, "is_superuser", False):
            return CommRole.SUPERADMIN

        if getattr(user, "is_staff", False):
            return CommRole.ADMIN

        return CommRole.CLIENT

    @staticmethod
    def _get_related_obj(*, obj: Any, field_name: str) -> Any:
        """
        Safely return a related object without relying on Django _id fields.
        """
        return getattr(obj, field_name, None)