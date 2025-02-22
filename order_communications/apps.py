from django.apps import AppConfig


class OrderCommunicationsConfig(AppConfig):
    """
    Configuration class for the Order Communications app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "order_communications"

    def ready(self):
        """
        Import signals when the app is ready.
        """
        import order_communications.signals  # Ensures signals are loaded