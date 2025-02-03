from django.apps import AppConfig


class TicketingSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'  # Replace with your app's name if different
    verbose_name = 'Ticketing System'

    def ready(self):
        # Import signals so they are registered when the app is ready
        import tickets.signals  # Ensure the signals module is imported
