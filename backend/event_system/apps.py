from django.apps import AppConfig

from event_system.registrations.review import register_review_events
from event_system.registrations.governance import register_governance_events


class EventSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event_system"

    def ready(self) -> None:

        register_review_events()
        register_governance_events()