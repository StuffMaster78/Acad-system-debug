from __future__ import annotations

from django.db import transaction

from tips.models.tip_outbox_event import TipOutboxEvent


class TipOutboxRequeueService:

    STATUS_PENDING = "pending"

    @classmethod
    @transaction.atomic
    def requeue(
        cls,
        *,
        outbox_event: TipOutboxEvent,
        triggered_by,
    ) -> TipOutboxEvent:

        # enforce correct state transitions
        if outbox_event.status == "sent":
            return outbox_event

        outbox_event.status = cls.STATUS_PENDING
        outbox_event.retry_count = (
            outbox_event.retry_count + 1
        )

        outbox_event.save(
            update_fields=["status", "retry_count"]
        )

        return outbox_event