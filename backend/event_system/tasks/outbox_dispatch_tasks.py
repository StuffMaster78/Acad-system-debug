from event_system.services.event_dispatcher_service import (
    EventDispatcherService,
)


def dispatch_outbox_events() -> None:
    """
    Periodic outbox dispatcher.

    Runs via Celery beat or cron.
    """

    EventDispatcherService.dispatch_pending()