from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
    verbose_name = "Payments"

    def ready(self):
        # Import signals if/when you actually use them
        try:
            import payments_processor.signals.handlers  # noqa
        except ImportError:
            pass