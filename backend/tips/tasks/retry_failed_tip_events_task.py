from __future__ import annotations

from celery import shared_task

from django.utils import timezone

from tips.models.tip_outbox_event import TipOutboxEvent


@shared_task
def retry_failed_tip_events_task() -> int:
    """
    Requeues retryable failed events.
    """

    now = timezone.now()

    updated = (
        TipOutboxEvent.objects
        .filter(
            processed=False,
            next_retry_at__lte=now,
        )
        .update(
            next_retry_at=None,
        )
    )

    return updated