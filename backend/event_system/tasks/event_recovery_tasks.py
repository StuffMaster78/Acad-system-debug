from django.utils import timezone
from datetime import timedelta

from event_system.models.event_outbox import EventOutbox, EventStatus


def reset_stuck_processing_events():
    """
    Safety net for crashed workers.
    """

    timeout = timezone.now() - timedelta(minutes=10)

    EventOutbox.objects.filter(
        status=EventStatus.PROCESSING,
        updated_at__lt=timeout,
    ).update(
        status=EventStatus.PENDING,
    )