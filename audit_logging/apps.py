from django.apps import AppConfig
import sys


class AuditLoggingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit_logging'

    def ready(self):
        # Avoid registering signals during migrations so we don't touch
        # ContentType or other tables before they exist.
        if any(cmd in sys.argv for cmd in ("migrate", "makemigrations")):
            return
        import audit_logging.signals  # Hook signals