from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Default primary key field type
    name = 'core'  # The name of the app

    def ready(self):
        """
        This method is called when the app is ready.
        You can use it to import signals or perform initialization tasks.
        """
        try:
            import core.signals  # noqa: F401
            import core.signals.config_versioning  # noqa: F401
            import users.signals  # noqa: F401
        except ImportError:
            pass
