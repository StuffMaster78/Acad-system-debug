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
        import communications.signals  # Ensures signals are loaded