from django.db import transaction
from django.utils import timezone

from event_system.models.event_outbox import EventOutbox, EventStatus


class EventClaimService:
    """
    Prevents multiple workers from processing the same event.

    Uses DB-level atomic update.
    """

    @classmethod
    def claim(cls, event_id: str) -> EventOutbox | None:
        """
        Atomically claim event for processing.

        Returns:
            EventOutbox if successfully claimed
            None if already taken
        """

        with transaction.atomic():
            updated = (
                EventOutbox.objects
                .select_for_update(skip_locked=True)
                .filter(
                    id=event_id,
                    status=EventStatus.PENDING,
                )
                .update(
                    status=EventStatus.PROCESSING,
                    updated_at=timezone.now(),
                )
            )

            if updated == 0:
                return None

            return EventOutbox.objects.get(id=event_id)