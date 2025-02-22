from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        """
        Override the ready method to import signals and ensure they are registered.
        """
        import orders.signals  # Import signals to connect them when the app is ready