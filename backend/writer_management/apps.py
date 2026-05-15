from django.apps import AppConfig


class WriterManagementConfig(AppConfig):
    name = "writer_management"
    verbose_name = "Writer Management"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """
        Register all signals when the app is ready.
        Import order matters — models must be loaded before signals.
        """
        import writer_management.signals  # noqa: F401