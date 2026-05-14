from event_system.services.event_dispatcher_service import (
    EventDispatcherService,
)


def process_event_batch() -> None:
    """
    Batch process event outbox safely.
    """

    EventDispatcherService.dispatch_pending(limit=200)