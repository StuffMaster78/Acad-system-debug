from __future__ import annotations

import logging
import os

log = logging.getLogger("config")


class RemoteConfig:
    """
    In-memory config overlay loaded from the database at startup.

    When REMOTE_CONFIG=true, all active global ConfigItem rows are loaded
    into memory once at boot. This gives services a fast dict lookup for
    config values without hitting the database on every request.

    The ConfigService (config_system.services.config_service) is still the
    canonical runtime accessor — it checks Redis → DB → default. RemoteConfig
    is an optional pre-warm layer that seeds the boot-time in-memory store.

    Refresh:
        Call remote_config.fetch() again from a Celery periodic task to
        pick up config changes without a deploy. The in-memory dict is
        replaced atomically.
    """

    def __init__(self):
        self.enabled = os.getenv("REMOTE_CONFIG", "false").strip().lower() in ("1", "true", "yes")
        self.store: dict[str, object] = {}

    def fetch(self) -> None:
        """
        Load all active global ConfigItem rows into the in-memory store.

        Safe to call at any time — errors are logged and silently ignored
        so a bad database state never prevents the app from starting.
        """
        if not self.enabled:
            return

        try:
            from config_system.storage.models import ConfigItem

            items = ConfigItem.objects.filter(
                is_active=True,
                scope="global",
            ).values("key", "value")

            self.store = {row["key"]: row["value"] for row in items}

            log.info(
                "RemoteConfig: loaded %d global config items from database.",
                len(self.store),
            )
        except Exception as exc:
            log.warning(
                "RemoteConfig.fetch() failed — continuing with empty store: %s", exc
            )
            self.store = {}

    def get(self, key: str, default=None):
        """Return a value from the in-memory config store."""
        return self.store.get(key, default)

    def reload(self) -> int:
        """
        Reload config from the database and return the number of items loaded.
        Useful as a Celery task target or admin action.
        """
        self.fetch()
        return len(self.store)


remote_config = RemoteConfig()
