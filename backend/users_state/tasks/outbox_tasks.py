from celery import shared_task

from notifications_system.models.outbox import Outbox


@shared_task
def create_outbox_entry(payload: dict):
    """
    Writes notification outbox entry.

    This is the only DB-write responsibility layer for notifications.
    """

    outbox, created = Outbox.objects.get_or_create(
        dedupe_key=payload["dedupe_key"],
        defaults={
            "event_key": payload["event_key"],
            "user_id": payload["recipient_id"],
            "website_id": payload["website_id"],
            "payload": payload,
        },
    )

    if not created:
        return None

    from notifications_system.tasks.send import process_outbox_entry

    outbox_id = outbox.id  # type: ignore[attr-defined]

    process_outbox_entry.delay(outbox_id)

    return outbox_id