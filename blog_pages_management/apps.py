from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BlogConfig(AppConfig):
    """
    Blog app configuration.
    - Loads signals for auto-processing.
    - Enables verbose app name in Django Admin.
    - Explicitly sets models_module to use models.py directly.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog_pages_management"
    verbose_name = _("Blog Management")
    # Explicitly use models.py instead of models/ package
    models_module = None  # Will be set to blog_pages_management.models (the .py file)

    def ready(self):
        """
        Auto-loads signals when the app is ready.
        - This ensures background tasks like analytics tracking work.
        """
        import blog_pages_management.signals  # Ensures signals are registered
        
    def import_models(self):
        """Import models from models.py and models/ submodules"""
        super().import_models()
        # Also import submodule models
        try:
            from . import models as models_package
            # Register submodule models that aren't in models.py
            # This is handled automatically if they're imported in models/__init__.py
            pass
        except ImportError:
            pass
