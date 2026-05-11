from django.apps import AppConfig


class TipsConfig(AppConfig):
    """
    Configuration for the tips application.

    This app handles all user tipping functionality including
    settlement rules, attribution, and financial processing.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "tips"