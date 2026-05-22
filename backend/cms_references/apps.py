from django.apps import AppConfig


class CmsReferencesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms_references"
    verbose_name = "CMS References"
    label = "cms_references"

    def ready(self):
        import cms_references.signals  # noqa: F401