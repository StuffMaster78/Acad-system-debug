from django.apps import AppConfig


class WebsitesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'websites'

    def ready(self):
        # Import signals to auto-populate academic settings on Website creation
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid crashing app startup on optional import errors
            pass
