from __future__ import annotations

from typing import Any

import logging
from django.conf import settings
from communications.sse.event_bus import (
    CommunicationSSEEventBus,
)
from communications.sse.event_formatter import (
    CommunicationSSEEventFormatter,
)

log = logging.getLogger(__name__)


class CommunicationEventService:
    """
    Publish communication events to delivery channels.

    For now this publishes to the in-process SSE bus.
    Later, swap internals to Redis pub/sub without changing callers.
    """

    @staticmethod
    def publish(
        *,
        event_type: str,
        payload: dict[str, Any],
        recipient_user_ids: list[int],
        website_id: int | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        """
        Publish a communication event.
        """
        resolved_meta = {
            **(meta or {}),
            "website_id": website_id,
            "recipient_user_ids": recipient_user_ids,
        }

        event = CommunicationSSEEventFormatter.build_event(
            event_type=event_type,
            payload=payload,
            meta=resolved_meta,
        )

        if getattr(settings, "DISABLE_COMMUNICATION_EVENTS", False):
            return

        try:
            CommunicationSSEEventBus.publish(event=event)
        except Exception as exc:
            log.warning(
                "Communication event publish failed: %s",
                exc,
            )

    @staticmethod
    def message_created(*, message, recipient_user_ids: list[int]) -> None:
        """
        Publish message created event.
        """
        CommunicationEventService.publish(
            event_type="communication.message.created",
            website_id=message.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": message.thread_id,
                "message_id": message.id,
                "sender_id": (
                    message.sender.id
                    if message.sender is not None
                    else None
                ),
                "status": message.status,
                "created_at": message.created_at.isoformat(),
            },
        )

    @staticmethod
    def message_updated(*, message, recipient_user_ids: list[int]) -> None:
        """
        Publish message updated event.
        """
        CommunicationEventService.publish(
            event_type="communication.message.updated",
            website_id=message.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": message.thread_id,
                "message_id": message.id,
                "status": message.status,
                "updated_at": message.updated_at.isoformat(),
            },
        )

    @staticmethod
    def message_hidden(*, message, recipient_user_ids: list[int]) -> None:
        """
        Publish message hidden event.
        """
        CommunicationEventService.publish(
            event_type="communication.message.hidden",
            website_id=message.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": message.thread_id,
                "message_id": message.id,
                "hidden_at": (
                    message.hidden_at.isoformat()
                    if message.hidden_at is not None
                    else None
                ),
            },
        )

    @staticmethod
    def message_withdrawn(*, message, recipient_user_ids: list[int]) -> None:
        """
        Publish message withdrawn event.
        """
        CommunicationEventService.publish(
            event_type="communication.message.withdrawn",
            website_id=message.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": message.thread_id,
                "message_id": message.id,
                "withdrawn_at": (
                    message.withdrawn_at.isoformat()
                    if message.withdrawn_at is not None
                    else None
                ),
            },
        )

    @staticmethod
    def thread_updated(*, thread, recipient_user_ids: list[int]) -> None:
        """
        Publish thread updated event.
        """
        CommunicationEventService.publish(
            event_type="communication.thread.updated",
            website_id=thread.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": thread.id,
                "status": thread.status,
                "last_message_at": (
                    thread.last_message_at.isoformat()
                    if thread.last_message_at is not None
                    else None
                ),
            },
        )

    @staticmethod
    def moderation_flag_created(
        *,
        flag,
        recipient_user_ids: list[int],
    ) -> None:
        """
        Publish moderation flag created event.
        """
        CommunicationEventService.publish(
            event_type="communication.moderation.flag.created",
            website_id=flag.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "flag_id": flag.id,
                "thread_id": flag.thread_id,
                "message_id": flag.message_id,
                "severity": flag.severity,
                "status": flag.status,
            },
        )

    @staticmethod
    def link_review_created(
        *,
        review,
        recipient_user_ids: list[int],
    ) -> None:
        """
        Publish link review created event.
        """
        CommunicationEventService.publish(
            event_type="communication.link_review.created",
            website_id=review.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "review_id": review.id,
                "thread_id": review.thread_id,
                "message_id": review.message_id,
                "domain": review.domain,
                "status": review.status,
            },
        )

    @staticmethod
    def message_read(
        *,
        message,
        reader,
        receipt,
        recipient_user_ids: list[int],
    ) -> None:
        """
        Publish message read event.
        """
        CommunicationEventService.publish(
            event_type="communication.message.read",
            website_id=message.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": message.thread_id,
                "message_id": message.pk,
                "reader_id": reader.pk,
                "receipt_id": receipt.pk,
                "read_at": receipt.read_at.isoformat(),
            },
        )

    @staticmethod
    def thread_read(
        *,
        thread,
        reader,
        recipient_user_ids: list[int],
    ) -> None:
        """
        Publish thread read event.
        """
        CommunicationEventService.publish(
            event_type="communication.thread.read",
            website_id=thread.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": thread.pk,
                "reader_id": reader.pk,
            },
        )


    @staticmethod
    def message_delivered(
        *,
        message,
        recipient,
        receipt,
        recipient_user_ids: list[int],
    ) -> None:
        """
        Publish message delivered event.
        """
        CommunicationEventService.publish(
            event_type="communication.message.delivered",
            website_id=message.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "thread_id": message.thread_id,
                "message_id": message.pk,
                "recipient_id": recipient.pk,
                "receipt_id": receipt.pk,
                "delivered_at": receipt.delivered_at.isoformat(),
            },
        )


    @staticmethod
    def attachment_added(
        *,
        attachment,
        recipient_user_ids: list[int],
    ) -> None:
        """
        Publish attachment added event.
        """
        CommunicationEventService.publish(
            event_type="communication.attachment.added",
            website_id=attachment.website_id,
            recipient_user_ids=recipient_user_ids,
            payload={
                "attachment_id": attachment.pk,
                "thread_id": attachment.thread_id,
                "message_id": attachment.message_id,
                "file_id": attachment.file_id,
                "requires_moderation": attachment.requires_moderation,
                "is_visible": attachment.is_visible,
            },
        )
