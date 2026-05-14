from django.apps import AppConfig

from event_system.router.event_router import EventRouter
from event_system.consumers.review_event_consumer import ReviewEventConsumer


class EventSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event_system"

    def ready(self) -> None:
        routes = getattr(ReviewEventConsumer, "ROUTES", {})

        for event_type, handler in routes.items():
            EventRouter.register(event_type, handler)