from django.apps import AppConfig
import logging

log = logging.getLogger(__name__)

class OrdersConfig(AppConfig):
    name = "orders"
    verbose_name = "Orders"

    def ready(self):
        # 1) load actions
        from . import actions
        loaded = actions.autodiscover()

         # Optional: show what actually registered (works with your decorator registry)
        try:
            # If your decorator keeps a module-level registry, expose a getter:
            # from orders.registry.decorator import get_registered_action_keys
            # keys = sorted(get_registered_action_keys())
            from orders.registry.decorator import get_all_registered_actions  # adjust name to yours
            keys = sorted(get_all_registered_actions().keys())  # e.g. {'approve_order': <class ...>, ...}
        except Exception:
            keys = []

        if not keys:
            log.warning(
                "[actions] %s orders.actions.base is loaded but no valid actions found. "
                "Imported modules: %s",
                "orders.actions.base",
                ", ".join(loaded) or "<none>",
            )
        else:
            log.info("[actions] loaded: %s", ", ".join(sorted(keys)))
