from django.apps import AppConfig

class ActivityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "activity"

    def ready(self):
        """Import signals when the app is ready."""
        import activity.signals  # Ensures signals are registered