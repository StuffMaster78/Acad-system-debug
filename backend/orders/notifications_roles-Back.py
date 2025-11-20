from __future__ import annotations

from typing import Any, Mapping, Optional

from notifications_system.registry.role_registry import register_role


def _user_model():
    """Return the configured User model (lazy import)."""
    from django.contrib.auth import get_user_model  # local import
    return get_user_model()


def _order(ctx: Mapping[str, Any]) -> Any:
    """Extract order object from context."""
    return ctx.get("order")


def resolve_client(ctx: Mapping[str, Any]) -> Optional[Any]:
    """Resolve the client user for an order context.

    Args:
        ctx: Event context expected to contain 'order'.

    Returns:
        The client user or None.
    """
    o = _order(ctx)
    return getattr(o, "client", None) if o else None


def resolve_writer(ctx: Mapping[str, Any]) -> Optional[Any]:
    """Resolve the writer user for an order context.

    Args:
        ctx: Event context expected to contain 'order'.

    Returns:
        The writer user or None.
    """
    o = _order(ctx)
    return getattr(o, "writer", None) if o else None


def resolve_support(ctx: Mapping[str, Any]) -> Optional[Any]:
    """Resolve a support user.

    Picks the first staff user deterministically to avoid costly random
    ordering. Replace with your routing logic if needed.
    """
    User = _user_model()
    return User.objects.filter(is_staff=True).first()


def resolve_admin(ctx: Mapping[str, Any]) -> Optional[Any]:
    """Resolve an admin user (first staff)."""
    User = _user_model()
    return User.objects.filter(is_staff=True).first()


def resolve_super_admin(ctx: Mapping[str, Any]) -> Optional[Any]:
    """Resolve a superuser."""
    User = _user_model()
    return User.objects.filter(is_superuser=True).first()


def resolve_editor(ctx: Mapping[str, Any]) -> Optional[Any]:
    """Resolve an editor (feature-flag/role field assumed)."""
    User = _user_model()
    return getattr(User.objects, "filter", lambda **k: User.objects.none())(
        is_editor=True
    ).first()


# ---- Role registrations -----------------------------------------------------
# Channel keys must use dotted event names; '*' is a wildcard fallback.

register_role(
    "client",
    resolver=resolve_client,
    channels={"*": {"in_app", "email"}},
)

register_role(
    "writer",
    resolver=resolve_writer,
    channels={
        "order.created": {"email", "in_app"},
        "order.assigned": {"email", "in_app", "webhook"},
        "*": {"in_app"},  # default for other writer events
    },
)

register_role(
    "support",
    resolver=resolve_support,
    channels={"*": {"email", "in_app", "ws"}},
)

register_role(
    "admin",
    resolver=resolve_admin,
    channels={"*": {"email", "in_app", "webhook"}},
)

register_role(
    "super_admin",
    resolver=resolve_super_admin,
    channels={"*": {"email", "in_app", "webhook", "sms"}},
)

register_role(
    "editor",
    resolver=resolve_editor,
    channels={"*": {"email", "in_app", "webhook", "sms", "telegram"}},
)