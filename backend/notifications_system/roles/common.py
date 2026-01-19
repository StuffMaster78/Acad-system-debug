# notifications_system/roles/common.py
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Set
from django.apps import apps
from django.conf import settings
from notifications_system.registry.role_registry import register_role

# ---- utilities -------------------------------------------------------------

def _user_model():
    return apps.get_model(settings.AUTH_USER_MODEL)

def _first(qs):
    try:
        return qs.first()
    except Exception:
        return None

def _obj_from(ctx: Mapping[str, Any], keys: tuple[str, ...]) -> Any | None:
    for k in keys:
        v = ctx.get(k)
        if v:
            return v
    return None

# ---- generic resolvers -----------------------------------------------------

def resolve_client(ctx: Mapping[str, Any]) -> Any | None:
    """
    Try to pull a client-like user from context objects, in order.
    Looks under keys like 'order', 'wallet', 'ticket'.
    """
    obj = _obj_from(ctx, ("order", "wallet", "ticket", "payment"))
    return getattr(obj, "client", None) if obj else None

def resolve_writer(ctx: Mapping[str, Any]) -> Any | None:
    """Mirror of resolve_client for a writer-like relation."""
    obj = _obj_from(ctx, ("order", "ticket"))
    if not obj:
        return None
    return getattr(obj, "assigned_writer", None) or getattr(obj, "writer", None)

def resolve_support(ctx: Mapping[str, Any]) -> Any | None:
    """Pick any staff user (or refine per project rules)."""
    U = _user_model()
    return _first(U.objects.filter(is_staff=True).order_by("id"))

def resolve_admin(ctx: Mapping[str, Any]) -> Any | None:
    """Admin fallback (first staff)."""
    U = _user_model()
    return _first(U.objects.filter(is_staff=True).order_by("id"))

def resolve_super_admin(ctx: Mapping[str, Any]) -> Any | None:
    U = _user_model()
    return _first(U.objects.filter(is_superuser=True).order_by("id"))

def resolve_editor(ctx: Mapping[str, Any]) -> Any | None:
    U = _user_model()
    # Adjust to your field/perm
    return _first(getattr(U.objects, "filter")(is_editor=True))

# ---- one-call registrar ----------------------------------------------------

def register_common_roles(
    *,
    # Optional per-role channel overrides for this app
    overrides: Dict[str, Dict[str, Set[str]]] | None = None,
    # Optional extra roles: {"qa": (resolver, {"*": {"in_app"}})}
    extra_roles: Dict[str, tuple] | None = None,
) -> None:
    """Register the standard roles + your local overrides.

    Args:
      overrides: role -> {event_key|\"*\" -> set(channels)}.
      extra_roles: role -> (resolver, channels_mapping).

    Notes:
      Project-wide defaults from settings.NOTIFICATION_ROLE_DEFAULTS
      still apply via the role registry merge.
    """
    ov = overrides or {}
    register_role("client", resolve_client, ov.get("client"))
    register_role("writer", resolve_writer, ov.get("writer"))
    register_role("support", resolve_support, ov.get("support"))
    register_role("admin", resolve_admin, ov.get("admin"))
    register_role("super_admin", resolve_super_admin, ov.get("super_admin"))
    register_role("editor", resolve_editor, ov.get("editor"))

    for role, spec in (extra_roles or {}).items():
        resolver, chans = spec
        register_role(role, resolver, chans or {})