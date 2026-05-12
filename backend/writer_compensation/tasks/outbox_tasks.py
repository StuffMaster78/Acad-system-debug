from __future__ import annotations

from celery import shared_task

from writer_compensation.services.outbox_dispatcher import (
    OutboxDispatcher,
)


@shared_task
def process_outbox_events(limit: int = 100) -> None:
    """
    Processes pending outbox events.

    Runs safely in background worker.
    """
    OutboxDispatcher.process_batch(limit=limit)