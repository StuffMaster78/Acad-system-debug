from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.constants import (
    CommunicationMessageStatus,
)
from communications.models.audit import (
    CommunicationAuditAction,
)
from communications.models.message import (
    CommunicationMessage,
    CommunicationMessageType,
)
from communications.services.audit_service import (
    CommunicationAuditService,
)
from communications.services.message_screening_service import (
    CommunicationMessageScreeningService,
)
from communications.services.sla_service import (
    CommunicationThreadSLAService,
)
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)
from communications.sse.event_bus import CommunicationSSEEventBus
from communications.services.event_recipient_service import (
    CommunicationEventRecipientService,
)
from communications.services.event_service import (
    CommunicationEventService,
)
from communications.validators import CommunicationMessageValidator
from communications.services.notification_service import (
    CommunicationNotificationService,
)


class CommunicationMessageService:
    """
    Service for creating and managing communication messages.

    This is the only approved place for user created messages.
    """

    @staticmethod
    @transaction.atomic
    def create_message(
        *,
        thread,
        sender,
        body: str,
        website=None,
        parent=None,
        message_type: str = CommunicationMessageType.USER,
        is_internal: bool = False,
        metadata: dict | None = None,
        ip_address: str | None = None,
        user_agent: str = "",
    ) -> CommunicationMessage:
        """
        Create a message in a thread.

        All user facing message creation must pass through this method.
        """
        resolved_website = website or thread.website

        CommunicationMessageService._validate_thread_website(
            thread=thread,
            website=resolved_website,
        )

        CommunicationThreadGuardService.enforce_can_send_message(
            user=sender,
            website=resolved_website,
            thread=thread,
        )
        CommunicationMessageValidator.validate_body(body=body)

        message = CommunicationMessage.objects.create(
            website=resolved_website,
            thread=thread,
            sender=sender,
            body=body,
            parent=parent,
            message_type=message_type,
            is_internal=is_internal,
            is_system_generated=False,
            status=CommunicationMessageStatus.ACTIVE,
            metadata=metadata or {},
        )

        screening = CommunicationMessageScreeningService.screen(
            message_body=body,
            message=message,
            actor=sender,
        )

        update_fields = ["updated_at"]

        if screening.cleaned_text != body:
            message.body = screening.cleaned_text
            update_fields.append("body")

        if screening.flagged:
            message.status = CommunicationMessageStatus.FLAGGED
            message.metadata = {
                **message.metadata,
                "screening": {
                    "has_phone": screening.has_phone,
                    "has_email": screening.has_email,
                    "has_link": screening.has_link,
                    "flagged": screening.flagged,
                },
            }
            update_fields.extend(["status", "metadata"])

        if len(update_fields) > 1:
            message.save(update_fields=update_fields)

        CommunicationMessageService._touch_thread(thread=thread)

        CommunicationThreadSLAService.update_on_message(
            thread=thread,
            sender_role=CommunicationMessageService._resolve_sender_role(
                sender=sender,
            ),
        )

        CommunicationAuditService.log(
            website=resolved_website,
            thread=thread,
            message=message,
            actor=sender,
            action=CommunicationAuditAction.MESSAGE_CREATED,
            details={
                "message_id": message.pk,
                "message_type": message.message_type,
                "status": message.status,
                "is_internal": message.is_internal,
                "screening": {
                    "has_phone": screening.has_phone,
                    "has_email": screening.has_email,
                    "has_link": screening.has_link,
                    "flagged": screening.flagged,
                },
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        recipient_user_ids = (
        CommunicationEventRecipientService.message_created_recipients(
                message=message,
            )
        )

        transaction.on_commit(lambda: CommunicationEventService.message_created(
            message=message,
            recipient_user_ids=recipient_user_ids,
        ))

        CommunicationEventService.thread_updated(
            thread=thread,
            recipient_user_ids=recipient_user_ids,
        )
        transaction.on_commit(
            lambda: CommunicationNotificationService.notify_message_created(
                message=message,
            ),
        )

        return message

    @staticmethod
    @transaction.atomic
    def create_system_message(
        *,
        thread,
        body: str,
        website=None,
        metadata: dict | None = None,
    ) -> CommunicationMessage:
        """
        Create a system generated message.
        """
        resolved_website = website or thread.website

        CommunicationMessageService._validate_thread_website(
            thread=thread,
            website=resolved_website,
        )

        message = CommunicationMessage.objects.create(
            website=resolved_website,
            thread=thread,
            sender=None,
            body=body,
            message_type=CommunicationMessageType.SYSTEM,
            is_internal=False,
            is_system_generated=True,
            status=CommunicationMessageStatus.ACTIVE,
            metadata=metadata or {},
        )

        CommunicationMessageService._touch_thread(thread=thread)

        CommunicationAuditService.log(
            website=resolved_website,
            thread=thread,
            message=message,
            actor=None,
            action=CommunicationAuditAction.MESSAGE_CREATED,
            details={
                "message_id": message.pk,
                "message_type": message.message_type,
                "status": message.status,
                "system_generated": True,
            },
        )

        return message

    @staticmethod
    @transaction.atomic
    def create_internal_note(
        *,
        thread,
        sender,
        body: str,
        website=None,
        metadata: dict | None = None,
        ip_address: str | None = None,
        user_agent: str = "",
    ) -> CommunicationMessage:
        """
        Create an internal staff only note.
        """
        resolved_website = website or thread.website

        CommunicationMessageService._validate_thread_website(
            thread=thread,
            website=resolved_website,
        )

        CommunicationThreadGuardService.enforce_can_send_message(
            user=sender,
            website=resolved_website,
            thread=thread,
        )

        message = CommunicationMessage.objects.create(
            website=resolved_website,
            thread=thread,
            sender=sender,
            body=body,
            message_type=CommunicationMessageType.INTERNAL_NOTE,
            is_internal=True,
            is_system_generated=False,
            status=CommunicationMessageStatus.ACTIVE,
            metadata=metadata or {},
        )

        CommunicationMessageService._touch_thread(thread=thread)

        CommunicationAuditService.log(
            website=resolved_website,
            thread=thread,
            message=message,
            actor=sender,
            action=CommunicationAuditAction.MESSAGE_CREATED,
            details={
                "message_id": message.pk,
                "message_type": message.message_type,
                "status": message.status,
                "is_internal": True,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return message

    @staticmethod
    @transaction.atomic
    def mark_message_hidden(
        *,
        message,
        actor,
        reason: str = "",
    ) -> CommunicationMessage:
        """
        Hide a message from normal users.
        """
        message.status = CommunicationMessageStatus.HIDDEN
        message.hidden_at = timezone.now()
        message.save(
            update_fields=[
                "status",
                "hidden_at",
                "updated_at",
            ],
        )

        CommunicationMessageValidator.validate_can_hide(message=message)
        CommunicationAuditService.log(
            website=message.website,
            thread=message.thread,
            message=message,
            actor=actor,
            action=CommunicationAuditAction.MESSAGE_HIDDEN,
            details={"reason": reason},
        )

        recipient_user_ids = (
            CommunicationEventRecipientService.active_thread_participant_ids(
                thread=message.thread,
                exclude_user=actor,
            )
        )

        CommunicationEventService.message_hidden(
            message=message,
            recipient_user_ids=recipient_user_ids,
        )

        return message

    @staticmethod
    @transaction.atomic
    def withdraw_message(
        *,
        message,
        actor,
        reason: str = "",
    ) -> CommunicationMessage:
        """
        Withdraw a message.

        The message remains in the database and audit trail.
        """
        message.status = CommunicationMessageStatus.WITHDRAWN
        message.withdrawn_at = timezone.now()
        message.metadata = {
            **message.metadata,
            "withdrawn": True,
            "withdraw_reason": reason,
        }
        message.save(
            update_fields=[
                "status",
                "withdrawn_at",
                "metadata",
                "updated_at",
            ],
        )
        CommunicationMessageValidator.validate_can_withdraw(message=message)
        CommunicationAuditService.log(
            website=message.website,
            thread=message.thread,
            message=message,
            actor=actor,
            action=CommunicationAuditAction.MESSAGE_HIDDEN,
            details={
                "reason": reason,
                "withdrawn": True,
            },
        )

        recipient_user_ids = (
            CommunicationEventRecipientService.active_thread_participant_ids(
                thread=message.thread,
                exclude_user=actor,
            )
        )

        CommunicationEventService.message_withdrawn(
            message=message,
            recipient_user_ids=recipient_user_ids,
        )

        return message

    @staticmethod
    def _touch_thread(*, thread) -> None:
        """
        Update thread last activity time.
        """
        thread.last_message_at = timezone.now()
        thread.save(update_fields=["last_message_at", "updated_at"])

    @staticmethod
    def _validate_thread_website(*, thread, website) -> None:
        """
        Ensure message website matches thread website.
        """
        if thread.website_id != website.id:
            raise ValueError(
                "Thread website does not match message website."
            )

    @staticmethod
    def _resolve_sender_role(*, sender) -> str:
        """
        Resolve sender role for SLA tracking.
        """
        if sender is None:
            return "system"

        if getattr(sender, "is_superuser", False):
            return "superadmin"

        if getattr(sender, "is_admin", False):
            return "admin"

        if getattr(sender, "is_support", False):
            return "support"

        if getattr(sender, "is_writer", False):
            return "writer"

        return "client"