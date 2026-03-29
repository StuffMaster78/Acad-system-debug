from __future__ import annotations

import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NotificationsSystemConfig(AppConfig):
    """App configuration for the notifications system."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications_system"
    verbose_name = "Notifications System"

    def ready(self) -> None:
        """Initialize notification system startup hooks."""
        if os.getenv("ENABLE_NOTIFICATIONS", "1") != "1":
            logger.info("Notifications disabled in this environment.")
            return

        try:
            import redis  # noqa: F401
        except Exception:
            logger.warning("Redis client not available (acceptable in dev).")

        try:
            from . import checks  # noqa: F401
            from . import signals  # noqa: F401
        except Exception as exc:
            logger.warning(
                "Signals/checks load failed: %s",
                exc,
                exc_info=True,
            )

        try:
            from . import tasks  # noqa: F401
        except Exception as exc:
            logger.warning(
                "Failed to import notification tasks module: %s",
                exc,
                exc_info=True,
            )

        logger.info("Notifications system ready.")