from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.models.delivery import CommunicationDeliveryReceipt
from communications.services.event_recipient_service import (
    CommunicationEventRecipientService,
)
from communications.services.event_service import CommunicationEventService


class CommunicationDeliveryReceiptService:
    """
    Manage message delivery receipts.
    """

    @staticmethod
    @transaction.atomic
    def mark_message_delivered(
        *,
        message,
        user,
        website=None,
    ) -> CommunicationDeliveryReceipt:
        """
        Mark one message as delivered to a user.
        """
        resolved_website = website or message.website

        receipt, created = CommunicationDeliveryReceipt.objects.get_or_create(
            website=resolved_website,
            message=message,
            thread=message.thread,
            user=user,
            defaults={"delivered_at": timezone.now()},
        )

        if not created:
            receipt.delivered_at = timezone.now()
            receipt.save(update_fields=["delivered_at"])

        recipient_user_ids = (
            CommunicationEventRecipientService.active_thread_participant_ids(
                thread=message.thread,
                exclude_user=user,
            )
        )

        transaction.on_commit(
            lambda: CommunicationEventService.message_delivered(
                message=message,
                recipient=user,
                receipt=receipt,
                recipient_user_ids=recipient_user_ids,
            ),
        )

        return receipt

    @staticmethod
    @transaction.atomic
    def mark_thread_messages_delivered(
        *,
        thread,
        user,
        website=None,
    ) -> list[CommunicationDeliveryReceipt]:
        """
        Mark all thread messages as delivered for a user.
        """
        resolved_website = website or thread.website
        receipts: list[CommunicationDeliveryReceipt] = []

        messages = thread.messages.filter(
            website=resolved_website,
        ).exclude(sender=user)

        for message in messages:
            receipt, _ = CommunicationDeliveryReceipt.objects.get_or_create(
                website=resolved_website,
                message=message,
                thread=thread,
                user=user,
                defaults={"delivered_at": timezone.now()},
            )
            receipts.append(receipt)

        return receipts