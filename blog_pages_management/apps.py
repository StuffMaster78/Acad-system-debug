from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BlogConfig(AppConfig):
    """
    Blog app configuration.
    - Loads signals for auto-processing.
    - Enables verbose app name in Django Admin.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog_pages_management"
    verbose_name = _("Blog Management")

    def ready(self):
        """
        Auto-loads signals when the app is ready.
        - This ensures background tasks like analytics tracking work.
        """
        import blog_pages_management.signals  # Ensures signals are registered
