# notifications_system/apps.py
from __future__ import annotations

import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NotificationsSystemConfig(AppConfig):
    """AppConfig for the Notifications System.

    On startup we:
      1) Wire signals/checks.
      2) Autoload templates (central + per-app).
      3) Discover per-app role bindings.
      4) Load notification event configs.
      5) Load broadcast event configs (optional).
      6) Refresh legacy main_registry snapshot (optional).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications_system"
    verbose_name = "Notifications System"

    def ready(self) -> None:  # noqa: D401
        # 1) Signals / checks (must not raise)
        try:
            import notifications_system.signals  # noqa: F401
            import notifications_system.checks  # noqa: F401
        except Exception as exc:  # noqa: BLE001
            logger.warning("Signals/checks load failed: %s", exc, exc_info=True)

        # 2) Templates
        try:
            from .registry.template_registry import autoload_all_templates
            autoload_all_templates()
            logger.debug("Template registry autoloaded.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Template autoload failed: %s", exc, exc_info=True)

        # 3) Roles
        try:
            from .registry.role_registry import autodiscover_roles
            autodiscover_roles()
            logger.debug("Role bindings discovered.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Role autodiscover failed: %s", exc, exc_info=True)

        # 4) Notification events (JSON → NOTIFICATION_REGISTRY)
        try:
            from .registry.notification_event_loader import load_event_configs
            load_event_configs()
            logger.debug("Notification events loaded.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Event configs load failed: %s", exc, exc_info=True)

        # 5) Broadcast events (optional JSON loader)
        try:
            from .registry.broadcast_event_loader import (
                autoload_broadcast_events,
            )
            autoload_broadcast_events()
            logger.debug("Broadcast events loaded.")
        except Exception as exc:  # noqa: BLE001
            logger.info(
                "Broadcast events not loaded (optional): %s",
                exc,
                exc_info=True,
            )

        # 6) Legacy snapshot (optional; for older callers)
        try:
            from .registry.main_registry import notification_registry
            notification_registry.clear()
            count = notification_registry.refresh_from_notifications()
            logger.debug(
                "main_registry refreshed from NOTIFICATION_REGISTRY (%d).",
                count,
            )
        except Exception as exc:  # noqa: BLE001
            logger.info(
                "Legacy main_registry refresh skipped: %s",
                exc,
                exc_info=True,
            )
