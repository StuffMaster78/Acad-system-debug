from __future__ import annotations

"""
DEPRECATED shim — do not add logic here.

Use notifications_system.registry.role_registry instead.

This module re-exports the minimal API so legacy imports keep working:
- get_channels_for_role(event_key, role)
- register_role(role, resolver, channels)

Project-specific role resolvers and channel policies must live in each
app's `notifications_roles.py` and be discovered via
role_registry.autodiscover_roles() from AppConfig.ready().
"""

from typing import Any, Mapping, Optional, Set

from .role_registry import (
    register_role as _register_role,
    get_channels_for_role as _get_channels_for_role,
)


def get_channels_for_role(event_key: str, role: Optional[str]) -> Set[str]:
    """Back-compat wrapper. Prefer role_registry.get_channels_for_role.

    Args:
        event_key: Canonical event key.
        role: Role name or None.

    Returns:
        Set of channel strings (may be empty).
    """
    return _get_channels_for_role(event_key, role)


def register_role(
    role: str,
    resolver,
    channels: Optional[Mapping[str, Set[str]]] = None,
) -> None:
    """Back-compat wrapper. Prefer role_registry.register_role.

    Args:
        role: Role name.
        resolver: Callable mapping context -> user.
        channels: Optional mapping of event_key -> set(channels).
    """
    _register_role(role, resolver, dict(channels or {}))


__all__ = ["get_channels_for_role", "register_role"]