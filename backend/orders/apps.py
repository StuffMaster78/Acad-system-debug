from __future__ import annotations

import os
import logging
from django.apps import AppConfig
from django.conf import settings

log = logging.getLogger(__name__)


class OrdersConfig(AppConfig):
    """Django app config for Orders.

    Responsibilities:
      * Autodiscover and register action classes.
      * Do NOT import notification modules here. Roles/templates/handlers
        should be discovered centrally (e.g., in the notifications app)
        to avoid double registration under the dev autoreloader.
    """

    name = "orders"
    verbose_name = "Orders"

    def ready(self) -> None:
        """Run app startup hooks for actions only.

        In DEBUG, skip the first autoreloader pass to avoid duplicate work.
        """
        if settings.DEBUG and os.environ.get("RUN_MAIN") != "true":
            return
        from orders.registry.discover import auto_discover_order_actions
        count = auto_discover_order_actions()
        log.info("[orders] loaded %d actions", count)
        
        # 1) Actions autodiscovery (your existing mechanism)
        try:
            from . import actions  # local import to avoid import loops
            loaded = actions.autodiscover()
        except Exception as exc:  # pragma: no cover
            loaded = []
            log.exception("[orders] actions autodiscover failed: %s", exc)

        # Optional: list registered actions if helper is available.
        keys = []
        try:
            from orders.registry.decorator import (  # type: ignore
                get_all_registered_actions,
            )
            keys = sorted(get_all_registered_actions().keys())
        except Exception:
            pass

        if not keys:
            log.warning(
                "[orders.actions] base loaded but no actions found. "
                "Imported: %s",
                ", ".join(loaded) or "<none>",
            )
        else:
            log.info("[orders.actions] loaded: %s", ", ".join(keys))
