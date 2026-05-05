from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.models.audit import CommunicationAuditAction
from communications.models.receipt import CommunicationReadReceipt
from communications.services.audit_service import CommunicationAuditService
from communications.services.event_recipient_service import (
    CommunicationEventRecipientService,
)
from communications.services.event_service import CommunicationEventService
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)


class CommunicationReadReceiptService:
    """
    Manage message read receipts.

    Used for:
        - unread thread indicators
        - read ticks
        - message seen status
    """

    @staticmethod
    @transaction.atomic
    def mark_message_read(
        *,
        message,
        user,
        website=None,
    ) -> CommunicationReadReceipt:
        """
        Mark one message as read by a user.
        """
        resolved_website = website or message.website

        CommunicationThreadGuardService.enforce_can_view_thread(
            user=user,
            website=resolved_website,
            thread=message.thread,
        )

        receipt, created = CommunicationReadReceipt.objects.get_or_create(
            website=resolved_website,
            message=message,
            thread=message.thread,
            user=user,
            defaults={"read_at": timezone.now()},
        )

        if not created:
            receipt.read_at = timezone.now()
            receipt.save(update_fields=["read_at"])

        CommunicationAuditService.log(
            website=resolved_website,
            thread=message.thread,
            message=message,
            actor=user,
            action=CommunicationAuditAction.MESSAGE_READ,
            details={
                "receipt_id": receipt.pk,
                "created": created,
            },
        )

        recipient_user_ids = (
            CommunicationEventRecipientService.active_thread_participant_ids(
                thread=message.thread,
                exclude_user=user,
            )
        )

        transaction.on_commit(
            lambda: CommunicationEventService.message_read(
                message=message,
                reader=user,
                receipt=receipt,
                recipient_user_ids=recipient_user_ids,
            ),
        )

        return receipt

    @staticmethod
    @transaction.atomic
    def mark_thread_read(
        *,
        thread,
        user,
        website=None,
    ) -> list[CommunicationReadReceipt]:
        """
        Mark all readable thread messages as read by a user.
        """
        resolved_website = website or thread.website

        CommunicationThreadGuardService.enforce_can_view_thread(
            user=user,
            website=resolved_website,
            thread=thread,
        )

        messages = (
            thread.messages
            .filter(website=resolved_website)
            .exclude(sender=user)
            .order_by("created_at", "id")
        )

        receipts: list[CommunicationReadReceipt] = []

        for message in messages:
            receipt, created = CommunicationReadReceipt.objects.get_or_create(
                website=resolved_website,
                message=message,
                thread=thread,
                user=user,
                defaults={"read_at": timezone.now()},
            )

            if not created:
                receipt.read_at = timezone.now()
                receipt.save(update_fields=["read_at"])

            receipts.append(receipt)

        CommunicationAuditService.log(
            website=resolved_website,
            thread=thread,
            actor=user,
            action=CommunicationAuditAction.MESSAGE_READ,
            details={
                "thread_mark_read": True,
                "receipt_count": len(receipts),
            },
        )

        recipient_user_ids = (
            CommunicationEventRecipientService.active_thread_participant_ids(
                thread=thread,
                exclude_user=user,
            )
        )

        transaction.on_commit(
            lambda: CommunicationEventService.thread_read(
                thread=thread,
                reader=user,
                recipient_user_ids=recipient_user_ids,
            ),
        )

        return receipts