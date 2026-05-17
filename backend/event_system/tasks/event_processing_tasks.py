from __future__ import annotations

import logging
from celery import app as celery_app
from celery import shared_task

from event_system.models.event_outbox import EventOutbox
from event_system.router.event_router import EventRouter

logger = logging.getLogger(__name__)




@shared_task(
    name="event_system.process_event_batch",
    bind=True,
    max_retries=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def process_event_batch(self) -> None:
    """
    Batch processor for pending events.
    """

    events = EventOutbox.objects.filter(
        status="pending"
    ).order_by("created_at")[:200]

    for event in events:
        event.status = "processing"
        event.save(update_fields=["status"])

        celery_app.send_task(
            "process_event_task",
            args=[str(event.id)],
        )


@shared_task(
    name="process_event_task",
    bind=True,
    max_retries=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def process_event_task(self, event_id: str) -> None:
    """
    Process single event outbox entry.
    """

    event = EventOutbox.objects.get(id=event_id)

    if event.status == "processed":
        return

    event.status = "processing"
    event.save(update_fields=["status"])

    handler = EventRouter.get(event.event_type)

    if not handler:
        event.status = "skipped"
        event.save(update_fields=["status"])
        return

    try:
        handler(event)

        event.status = "processed"
        event.save(update_fields=["status"])

    except Exception as exc:
        logger.exception(
            "Event processing failed: %s",
            event.event_type,
        )

        event.status = "failed"
        event.save(update_fields=["status"])

        raise exc