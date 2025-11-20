from django.apps import AppConfig

class SuperadminManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'superadmin_management'
    verbose_name = "Superadmin Management"

    def ready(self):
        """
        Import signals when the app is ready.
        This ensures automated notifications & logging.
        """
        import superadmin_management.signals