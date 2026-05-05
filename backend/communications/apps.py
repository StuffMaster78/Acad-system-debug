from django.apps import AppConfig


class OrderCommunicationsConfig(AppConfig):
    """
    Configuration class for the Order Communications app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "communications"

    def ready(self):
        """
        Import signals when the app is ready.
        """
        from communications.integrations.setup import (
            register_communication_adapters,
        )

        register_communication_adapters()
        import communications.signals  # Ensures signals are loaded