"""
Holiday Management App Configuration
"""
from django.apps import AppConfig


class HolidayManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'holiday_management'
    verbose_name = 'Holiday Management'

    def ready(self):
        """Import signals when app is ready."""
        import holiday_management.signals  # noqa

