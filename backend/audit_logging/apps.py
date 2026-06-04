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
        _signal_modules = [
            "audit_logging.signals.model_signals",
            "audit_logging.signals.auth_signals",
            "audit_logging.signals.order_signals",
            "audit_logging.signals.billing_signals",
            "audit_logging.signals.config_signals",
        ]
        for _mod in _signal_modules:
            try:
                __import__(_mod)
            except Exception:
                pass
