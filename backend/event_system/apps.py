from django.apps import AppConfig


class EventSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event_system"

    def ready(self) -> None:
        try:
            from event_system.registrations.review import register_review_events
            from event_system.registrations.governance import (
                register_governance_events,
            )

            register_review_events()
            register_governance_events()
        except Exception:
            pass
