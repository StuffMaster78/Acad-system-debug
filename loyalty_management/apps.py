from django.apps import AppConfig


class LoyaltyManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loyalty_management'

    def ready(self):
        import loyalty_management.signals  # Import signals here