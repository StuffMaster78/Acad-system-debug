from __future__ import annotations

from django.apps import AppConfig


class ActivityConfig(AppConfig):
    """
    App configuration for platform activity events.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "activity"