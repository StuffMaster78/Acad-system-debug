from __future__ import annotations

from typing import Any, Dict, Iterable
from django.conf import settings


class NotificationSettings:
    """
    Central config accessors for the notifications system.
    Values are read from django.conf.settings on every access,
    so test overrides and env changes are picked up reliably.
    """

    # -------- Defaults (used if settings.* is missing) --------
    _DEFAULTS: Dict[str, Any] = {
        # Channels
        "NOTIFICATION_DEFAULT_CHANNELS": ["in_app", "email"],
        "NOTIFICATION_ENABLED_CHANNELS": {
            "in_app": True,
            "email": True,
            "sms": False,
            "push": True,
            "webhook": False,
            "telegram": False,
            "whatsapp": False,
            "sse": True,
            "ws": True,
        },

        # Retries / backoff
        "DEFAULT_MAX_RETRIES": 3,
        "USE_SYNC_RETRIES": False,
        "CHANNEL_BACKOFFS": {
            "email": 10,
            "sms": 10,
            "push": 5,
            "webhook": 15,
            "telegram": 8,
            "whatsapp": 8,
            "sse": 2,
        },

        # Async feature flags
        "USE_CELERY": False,
        "USE_ASYNC_EMAIL": False,
        "USE_ASYNC_SMS": False,
        "USE_ASYNC_PUSH": False,

        # Digests
        "NOTIFICATION_ENABLE_DIGESTS": True,

        # Global toggles
        "NOTIFICATION_DEBUG_MODE": False,
        "NOTIFICATION_DELIVERY_DELAY_SECONDS": 0,
        "NOTIFICATION_CRITICAL_CHANNELS": ["email", "push"],

        # Event config locations (for loaders)
        "NOTIFY_EVENTS_DIR": None,                 # e.g. BASE_DIR / "notifications_system/registry/configs"
        "NOTIFY_APP_EVENTS_SUBDIR": "notification_configs",

        # Broadcast / realtime
        "NOTIFICATION_ENABLE_BROADCASTS": True,
        "NOTIFICATION_ENABLE_REALTIME": True,      # controls SSE/WS publish
        "NOTIFICATION_REQUIRE_BROADCAST_ACK": False,

        # Misc
        "NOTIFICATION_SEND_RESET_EMAIL": True,
    }

    # ------------- helpers -------------
    @classmethod
    def _get(cls, key: str):
        return getattr(settings, key, cls._DEFAULTS[key])

    @classmethod
    def default_channels(cls) -> list[str]:
        return list(cls._get("NOTIFICATION_DEFAULT_CHANNELS"))

    @classmethod
    def enabled_channels(cls) -> Dict[str, bool]:
        # allow partial overrides in settings by merging dicts
        merged = dict(cls._DEFAULTS["NOTIFICATION_ENABLED_CHANNELS"])
        merged.update(getattr(settings, "NOTIFICATION_ENABLED_CHANNELS", {}) or {})
        return merged

    @classmethod
    def is_channel_enabled(cls, channel: str) -> bool:
        return bool(cls.enabled_channels().get(channel, False))

    # retries/backoff
    @classmethod
    def max_retries(cls) -> int:
        return int(cls._get("DEFAULT_MAX_RETRIES"))

    @classmethod
    def use_sync_retries(cls) -> bool:
        return bool(cls._get("USE_SYNC_RETRIES"))

    @classmethod
    def channel_backoff(cls, channel: str) -> int:
        backoffs = dict(cls._DEFAULTS["CHANNEL_BACKOFFS"])
        backoffs.update(getattr(settings, "CHANNEL_BACKOFFS", {}) or {})
        return int(backoffs.get(channel, 10))

    # async feature flags
    @classmethod
    def use_celery(cls) -> bool:
        return bool(cls._get("USE_CELERY"))

    @classmethod
    def use_async_email(cls) -> bool:
        return bool(cls._get("USE_ASYNC_EMAIL"))

    @classmethod
    def use_async_sms(cls) -> bool:
        return bool(cls._get("USE_ASYNC_SMS"))

    @classmethod
    def use_async_push(cls) -> bool:
        return bool(cls._get("USE_ASYNC_PUSH"))

    # digests
    @classmethod
    def enable_digests(cls) -> bool:
        return bool(cls._get("NOTIFICATION_ENABLE_DIGESTS"))

    # global toggles
    @classmethod
    def debug_mode(cls) -> bool:
        return bool(cls._get("NOTIFICATION_DEBUG_MODE"))

    @classmethod
    def delivery_delay_seconds(cls) -> int:
        return int(cls._get("NOTIFICATION_DELIVERY_DELAY_SECONDS"))

    @classmethod
    def critical_channels(cls) -> Iterable[str]:
        return list(cls._get("NOTIFICATION_CRITICAL_CHANNELS"))

    # event config locations
    @classmethod
    def events_dir(cls):
        return cls._get("NOTIFY_EVENTS_DIR")

    @classmethod
    def app_events_subdir(cls) -> str:
        return str(cls._get("NOTIFY_APP_EVENTS_SUBDIR"))

    # broadcasts / realtime
    @classmethod
    def enable_broadcasts(cls) -> bool:
        return bool(cls._get("NOTIFICATION_ENABLE_BROADCASTS"))

    @classmethod
    def enable_realtime(cls) -> bool:
        return bool(cls._get("NOTIFICATION_ENABLE_REALTIME"))

    @classmethod
    def require_broadcast_ack(cls) -> bool:
        return bool(cls._get("NOTIFICATION_REQUIRE_BROADCAST_ACK"))

    # misc
    @classmethod
    def send_reset_email(cls) -> bool:
        return bool(cls._get("NOTIFICATION_SEND_RESET_EMAIL"))