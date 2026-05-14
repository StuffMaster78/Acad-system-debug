from event_system.services.event_dispatcher_service import (
    EventDispatcherService,
)
from reviews_system.events.review_event_builder import (
    ReviewEvent,
)
from event_system.models.event_outbox import EventOutbox
from event_system.services.event_bus_service import (
    EventBusService,
)

def dispatch_review_event(event_data: dict) -> None:
    """
    Celery-safe task to dispatch review domain events.

    This keeps event emission out of request cycle.
    """

    event = ReviewEvent(
        event_type=event_data["event_type"],
        review_id=event_data["review_id"],
        target_type=event_data["target_type"],
        target_id=event_data["target_id"],
        actor_id=event_data.get("actor_id"),
        payload=event_data.get("payload", {}),
    )

    EventBusService.publish(event)