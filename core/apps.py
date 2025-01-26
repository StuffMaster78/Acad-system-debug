from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Default primary key field type
    name = 'core'  # The name of the app

    def ready(self):
        """
        This method is called when the app is ready.
        You can use it to import signals or perform initialization tasks.
        """
        import core.signals  # Import signals (if any) when the app is ready
