from django.apps import AppConfig


class OrderPaymentsManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "order_payments_management"

    def ready(self):
        """
        Imports signals when the app is ready.
        This ensures signals are correctly loaded on startup.
        """
        import order_payments_management.signals  # ✅ Import signals