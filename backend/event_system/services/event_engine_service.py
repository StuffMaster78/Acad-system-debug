from django.utils import timezone

from event_system.models.event_outbox import EventOutbox
from event_system.services.idempotency_service import IdempotencyService
from event_system.router.event_router import EventRouter


class EventEngine:
    """
    Single execution engine:
        - routing
        - execution
        - persistence updates
    """

    @classmethod
    def process(cls, event: EventOutbox) -> None:
        if IdempotencyService.is_processed(str(event.id)):
            event.status = "processed"
            event.save(update_fields=["status"])
            return

        try:
            handler = EventRouter.get(event.event_type)

            if handler is None:
                return

            handler(event)

            event.status = "processed"
            event.updated_at = timezone.now()
            event.save(update_fields=["status", "updated_at"])

            IdempotencyService.mark_processed(str(event.id))

        except Exception:
            event.attempts += 1
            event.status = "failed"
            event.save(update_fields=["attempts", "status"])
            raise