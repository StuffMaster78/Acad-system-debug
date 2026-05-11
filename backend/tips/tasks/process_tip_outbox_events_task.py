from __future__ import annotations

from celery import shared_task

from django.db import transaction
from django.utils import timezone

from tips.models.tip_outbox_event import TipOutboxEvent
from tips.workers.tip_outbox_worker import TipOutboxWorker


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def process_tip_outbox_events_task(self) -> int:
    """
    Processes pending outbox events safely.
    """

    processed_count = 0

    events = (
        TipOutboxEvent.objects
        .select_for_update(skip_locked=True)
        .filter(
            processed=False,
        )
        .filter(
            next_retry_at__isnull=True,
        )
        .order_by("created_at")[:100]
    )

    with transaction.atomic():

        for event in events:

            TipOutboxWorker.process(event)

            processed_count += 1

    return processed_count