# orders/notifications_roles.py
from __future__ import annotations

from typing import Any, Mapping, Optional
from django.contrib.auth import get_user_model
from notifications_system.registry.role_registry import register_role

User = get_user_model()


def _order(ctx: Mapping[str, Any]):
    return ctx.get("order")


def resolve_client(ctx: Mapping[str, Any]) -> Optional[User]:
    o = _order(ctx)
    return getattr(o, "client", None) if o else None


def resolve_writer(ctx: Mapping[str, Any]) -> Optional[User]:
    o = _order(ctx)
    return getattr(o, "writer", None) if o else None


def resolve_support(ctx: Mapping[str, Any]) -> Optional[User]:
    return User.objects.filter(is_staff=True).order_by("?").first()


def resolve_admin(ctx: Mapping[str, Any]) -> Optional[User]:
    return User.objects.filter(is_staff=True).first()


def resolve_super_admin(ctx: Mapping[str, Any]) -> Optional[User]:
    return User.objects.filter(is_superuser=True).first()


def resolve_editor(ctx: Mapping[str, Any]) -> Optional[User]:
    return User.objects.filter(is_editor=True).first()


register_role(
    "client",
    resolver=resolve_client,
    channels={"*": {"in_app", "email"}},
)

register_role(
    "writer",
    resolver=resolve_writer,
    channels={
        "order_created": {"email", "in_app"},
        "order_assigned": {"email", "in_app", "webhook"},
    },
)

register_role(
    "support",
    resolver=resolve_support,
    channels={"*": {"email", "in_app", "ws"}},  # use "ws", not "websocket"
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