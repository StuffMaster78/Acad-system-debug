from django.apps import AppConfig


class AuditLoggingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    name = "audit_logging"

    verbose_name = "Audit Logging"

    def ready(self):
        """
        Import signal registrations and startup hooks.
        Keep imports LOCAL to avoid app registry issues.
        """

        # future:
        # import audit_logging.signals  # noqa: F401
        import audit_logging.signals.model_signals