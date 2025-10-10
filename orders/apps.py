from __future__ import annotations

import logging
from django.apps import AppConfig

log = logging.getLogger(__name__)


class OrdersConfig(AppConfig):
    """Django app config for Orders.

    Responsibilities:
      * Autodiscover and register action classes.
      * Import notifications modules so their decorators run:
        - orders.notifications_roles (register_role)
        - orders.notification_templates (register_template)
        - orders.notification_handlers (@notification_handler)
    """

    name = "orders"
    verbose_name = "Orders"

    def ready(self) -> None:
        """Run app startup hooks for actions and notifications."""
        # --- 1) Actions autodiscovery (your existing mechanism) ----------
        try:
            from . import actions  # local import to avoid import loops
            loaded = actions.autodiscover()
        except Exception as exc:  # pragma: no cover
            loaded = []
            log.exception("[orders] actions autodiscover failed: %s", exc)

        # Optional visibility: list registered actions, if API is present
        keys = []
        try:
            from orders.registry.decorator import (  # type: ignore
                get_all_registered_actions,
            )
            keys = sorted(get_all_registered_actions().keys())
        except Exception:
            # It's fine if your registry helper is not available.
            pass

        if not keys:
            log.warning(
                "[orders.actions] base loaded but no actions found. Imported: %s",
                ", ".join(loaded) or "<none>",
            )
        else:
            log.info("[orders.actions] loaded: %s", ", ".join(keys))

        # --- 2) Notifications: import modules so decorators execute -------
        # These imports are idempotent; they only register once.
        try:
            # Roles -> register_role(...)
            from orders import notifications_roles  # noqa: F401
        except Exception as exc:  # pragma: no cover
            log.exception("[orders] load notifications_roles failed: %s", exc)

        try:
            # Class-based templates -> @register_template("order.*")
            from orders import notification_templates  # noqa: F401
        except Exception as exc:  # pragma: no cover
            log.exception("[orders] load notification_templates failed: %s", exc)

        try:
            # Handlers -> @notification_handler("order.*")
            from orders import notification_handlers  # noqa: F401
        except Exception as exc:  # pragma: no cover
            log.exception("[orders] load notification_handlers failed: %s", exc)

        # --- 3) (Optional) Log what registered for sanity ----------------
        try:
            from notifications_system.registry.role_registry import (
                list_registered_roles,
            )
            roles = list_registered_roles()
            log.info(
                "[orders.notifications] roles registered: %s",
                ", ".join(sorted(roles.keys())) or "<none>",
            )
        except Exception:
            # Role registry listing is optional.
            pass

        try:
            from notifications_system.registry.template_registry import (
                get_templates_for_event,
            )
            # Probe a few common events to help during dev.
            sample = ("order.paid", "order.assigned", "order.submitted")
            samples = {
                ev: get_templates_for_event(ev) for ev in sample
            }
            log.debug(
                "[orders.notifications] sample template names: %s",
                samples,
            )
        except Exception:
            # Template-name mapping is optional.
            pass