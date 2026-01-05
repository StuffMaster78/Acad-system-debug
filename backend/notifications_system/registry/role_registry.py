from __future__ import annotations

import importlib
import logging
from typing import Any, Callable, Dict, Mapping, Optional, Set

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)

# A resolver takes a context mapping (e.g., {"order": ...}) and returns
# a user instance (or None).
RoleResolver = Callable[[Mapping[str, Any]], Any]

# Registered role -> resolver callable.
ROLE_RESOLVERS: Dict[str, RoleResolver] = {}

# Registered role -> { event_key -> set(channels) }.
ROLE_CHANNELS: Dict[str, Dict[str, Set[str]]] = {}

# Optional project-level defaults from settings:
# NOTIFICATION_ROLE_DEFAULTS = {
#   "client": {"*": {"in_app", "email"}},
#   "admin":  {"order.created": {"email"}}
# }
DEFAULT_ROLE_CHANNELS: Dict[str, Dict[str, Set[str]]] = getattr(
    settings,
    "NOTIFICATION_ROLE_DEFAULTS",
    {},
)


def get_user_model():
    """Return the configured User model (lazy)."""
    return apps.get_model(settings.AUTH_USER_MODEL)


def register_role(
    role: str,
    resolver: RoleResolver,
    channels: Optional[Dict[str, Set[str]]] = None,
) -> None:
    """Register a role's resolver and (optional) event channel mapping.

    Args:
        role: Role name (e.g., "client", "admin").
        resolver: Callable that maps context -> user instance.
        channels: Mapping of event_key -> set of channels. Use "*" for
            a wildcard default for that role.

    Notes:
        * If re-registered, the prior resolver/channels are overwritten.
        * Provided channels are merged over project defaults.
    """
    if role in ROLE_RESOLVERS:
        # If the incoming registration is identical to the existing one,
        # treat it as a no-op to avoid noisy logs under auto-reload.
        existing_resolver = ROLE_RESOLVERS.get(role)
        existing_channels = ROLE_CHANNELS.get(role, {})
        incoming_channels = {k: set(v) for k, v in (channels or {}).items()}
        if existing_resolver is resolver and existing_channels == incoming_channels:
            logger.debug(
                "[notifications] Role '%s' already registered with identical config; skipping.",
                role,
            )
            return
        # Changed to DEBUG - this is expected behavior when apps override common roles
        logger.debug(
            "[notifications] Role '%s' already registered; overwriting.",
            role,
        )

    ROLE_RESOLVERS[role] = resolver

    merged: Dict[str, Set[str]] = {
        k: set(v) for k, v in DEFAULT_ROLE_CHANNELS.get(role, {}).items()
    }
    if channels:
        for event_key, chans in channels.items():
            merged[event_key] = set(chans)

    ROLE_CHANNELS[role] = merged or {"*": set()}


def resolve_role_user(role: str, context: Mapping[str, Any]) -> Any:
    """Resolve a user for a role using the provided context.

    Args:
        role: Role name.
        context: Mapping containing domain objects (e.g., 'order').

    Returns:
        User instance or None if no resolver/failed resolution.
    """
    resolver = ROLE_RESOLVERS.get(role)
    if not resolver:
        logger.warning("[notifications] No resolver for role '%s'", role)
        return None
    try:
        return resolver(context)
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "[notifications] Resolver for role '%s' raised: %s", role, exc
        )
        return None


def get_channels_for_role(event_key: str, role: Optional[str]) -> Set[str]:
    """Return channels configured for a role on a given event.

    Args:
        event_key: Canonical event key.
        role: Role name or None.

    Returns:
        Set of channel strings; may be empty.
    """
    if not role:
        return set()
    role_channels = ROLE_CHANNELS.get(role, {})
    return set(role_channels.get(event_key, role_channels.get("*", set())))


def autodiscover_roles() -> None:
    """Auto-import role shims and (optionally) common defaults.

    Behavior:
      1) If settings.NOTIFICATION_AUTOREGISTER_COMMON_ROLES is true
         (default), register common roles using optional project-level
         overrides from settings.NOTIFICATION_COMMON_ROLE_OVERRIDES.
      2) Import `<app>.notifications_roles` for each installed app.
         App modules may re-register roles; this intentionally overwrites
         previous resolvers/channels.
    """
    # 1) Optional common roles (project-level DRY defaults)
    try:
        auto = getattr(
            settings, "NOTIFICATION_AUTOREGISTER_COMMON_ROLES", True
        )
        if auto:
            from notifications_system.roles import register_common_roles

            overrides = getattr(
                settings, "NOTIFICATION_COMMON_ROLE_OVERRIDES", {}
            )
            register_common_roles(overrides=overrides)
            logger.debug(
                "[notifications] Registered common roles with overrides: %s",
                sorted(overrides.keys()) if overrides else "none",
            )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "[notifications] Failed registering common roles: %s", exc
        )

    # 2) Per-app shims: <app>.notifications_roles
    for app_config in apps.get_app_configs():
        mod = f"{app_config.name}.notifications_roles"
        try:
            importlib.import_module(mod)
            logger.debug("[notifications] Loaded roles from %s", mod)
        except ModuleNotFoundError as exc:
            if "notifications_roles" not in str(exc):
                logger.debug("Module not found: %s", mod)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "[notifications] Failed to load roles from %s: %s", mod, exc
            )

    # Optional visibility: what’s registered now?
    try:
        summary = list_registered_roles()
        logger.debug(
            "[notifications] Roles registered: %s",
            ", ".join(sorted(summary.keys())) or "<none>",
        )
    except Exception:  # pragma: no cover
        pass



def list_registered_roles() -> Dict[str, Dict[str, Any]]:
    """Return a serializable view of registered roles.

    Returns:
        Dict of role -> {"resolver": str, "channels": {event: [..], ...}}
    """
    out: Dict[str, Dict[str, Any]] = {}
    for role, resolver in ROLE_RESOLVERS.items():
        name = getattr(resolver, "__name__", str(resolver))
        channels = {k: sorted(v) for k, v in ROLE_CHANNELS.get(role, {}).items()}
        out[role] = {"resolver": name, "channels": channels}
    return out


def clear_role_registry() -> None:
    """Clear all registered roles and channels (tests/dev only)."""
    ROLE_RESOLVERS.clear()
    ROLE_CHANNELS.clear()
    logger.info("[notifications] Cleared role registry.")


__all__ = [
    "RoleResolver",
    "ROLE_RESOLVERS",
    "ROLE_CHANNELS",
    "register_role",
    "resolve_role_user",
    "get_channels_for_role",
    "autodiscover_roles",
    "list_registered_roles",
    "clear_role_registry",
    "get_user_model"
]