from django.apps import AppConfig


class ReputationSystemConfig(AppConfig):
    """
    Reputation system application config.

    Responsible for:
        - registering signals (if needed later)
        - bootstrapping event consumers
        - domain initialization hooks
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "reputation_system"

    def ready(self) -> None:
        """
        Import signal handlers / event consumers safely.
        Avoid heavy logic here.
        """

        # Import consumers to register handlers
        # IMPORTANT: keep lazy imports to avoid circular issues
        # try:
        # from reputation_system.events.reputation_event_consumer import (
        # register_reputation_event_consumer,
        # )

        # register_reputation_event_consumer()
        # except ImportError:
        # # Safe fallback for partial environments / migrations
        # pass