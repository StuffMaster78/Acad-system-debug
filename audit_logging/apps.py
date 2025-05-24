from django.apps import AppConfig


class AuditLoggingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit_logging'

    def ready(self):
        import audit_logging.signals  # Hook signals