from django.apps import AppConfig


class CmsCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms_core"
    verbose_name = "CMS Core"
    label = "cms_core"

    def ready(self):
        import cms_core.wagtail_hooks # noqa: F401