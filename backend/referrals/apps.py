from django.apps import AppConfig


class ReferralsConfig(AppConfig):
    """Application config for the referrals app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "referrals"

    def ready(self):
        """Import signal handlers."""
        import referrals.signals # noqa: F401
