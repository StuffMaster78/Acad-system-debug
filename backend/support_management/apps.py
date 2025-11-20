from django.apps import AppConfig


class SupportManagementConfig(AppConfig):
    """
    Configuration for the Support Management app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "support_management"

    def ready(self):
        """
        Import signals to ensure they are registered on app startup.
        """
        import support_management.signals 