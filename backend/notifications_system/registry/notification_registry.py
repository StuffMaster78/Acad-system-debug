"""
Notification Registry for the Notifications System.

This module manages the registration and retrieval of notification
events and their configurations. It provides a centralized registry
for event configs, allowing flexible and extensible notification
management.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from notifications_system.registry.notification_event_loader import load_event_configs
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# Global in-memory registry
from notifications_system.registry.main_registry import NOTIFICATION_REGISTRY
# NOTIFICATION_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_notification(force_reload: bool = False, **kwargs) -> None:
    """Register or reload notification configs.

    Args:
        force_reload (bool): If True, reload event configs from source.
        **kwargs: Ignored, kept for forward-compatibility.
    """
    # Always reload from sources to keep the registry fresh.
    config = load_event_configs()
    NOTIFICATION_REGISTRY.clear()
    NOTIFICATION_REGISTRY.update(config)

def bulk_register_notifications(force_reload: bool = False, **kwargs) -> None:
    """Bulk register or reload notification configs.

    Args:
        force_reload (bool): If True, reload event configs from source.
        **kwargs: Ignored, kept for forward-compatibility.
    """
    # Always reload from sources to keep the registry fresh.
    config = load_event_configs()
    NOTIFICATION_REGISTRY.clear()
    NOTIFICATION_REGISTRY.update(config)

def get_notification_config(event_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve config for a given event.

    Args:
        event_key (str): Unique event identifier.

    Returns:
        Optional[Dict[str, Any]]: Config dict if found, else None.
    """
    return NOTIFICATION_REGISTRY.get(event_key)


def get_digest_config(event_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve digest-specific config for a given event.

    Args:
        event_key (str): Unique event identifier.

    Returns:
        Optional[Dict[str, Any]]: Digest config dict if present, else None.
    """
    config = NOTIFICATION_REGISTRY.get(event_key)
    if not config:
        return None
    dig = config.get("digest")
    return dig if isinstance(dig, dict) else None


def list_all_event_keys() -> list[str]:
    """List all registered event keys.

    Returns:
        list[str]: List of all event identifiers.
    """
    return list(NOTIFICATION_REGISTRY.keys())

# Retrieval
def list_all_event_configs() -> Dict[str, Dict[str, Any]]:
    """List all registered event configs.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of all event configs.
    """
    return NOTIFICATION_REGISTRY.copy()

def get_handler_config(event_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve handler-specific config for a given event.

    Args:
        event_key (str): Unique event identifier.

    Returns:
        Optional[Dict[str, Any]]: Handler config dict if present, else None.
    """
    config = NOTIFICATION_REGISTRY.get(event_key)
    if not config:
        return None
    handler = config.get("handler")
    return handler if isinstance(handler, dict) else None


# --- Lightweight typed view of an event config ---
@dataclass(frozen=True)
class EventMeta:
    key: str
    label: str
    enabled: bool
    roles: List[str]
    priority: str
    channels: List[str]           # effective default channels
    templates: Dict[str, Any]     # whatever you keep in "templates"
    raw: Dict[str, Any]           # full normalized item


def _ensure_loaded() -> None:
    """
    Make sure the global NOTIFICATION_REGISTRY is populated.
    Keeps your existing registry + loader contract intact.
    """
    from notifications_system.registry.main_registry import NOTIFICATION_REGISTRY as _REG
    if not _REG:
        # Reuse your existing reload function
        register_notification(force_reload=True)


def _derive_channels(cfg: Dict[str, Any]) -> List[str]:
    """
    Prefer explicit 'channels'; else infer from template keys.
    """
    ch = cfg.get("channels") or []
    if isinstance(ch, (list, tuple)) and ch:
        # dedupe while preserving order
        seen = set()
        ordered = []
        for c in ch:
            if isinstance(c, str) and c not in seen:
                seen.add(c); ordered.append(c)
        return ordered

    tmpls = cfg.get("templates") or {}
    if isinstance(tmpls, dict) and tmpls:
        inferred = [k for k in tmpls.keys() if isinstance(k, str)]
        if inferred:
            return sorted(set(inferred))

    return []


def get_event(event_key: str) -> Optional[EventMeta]:
    """
    Typed accessor for a single event.
    Returns None if the key is missing or disabled.
    """
    if not event_key:
        return None

    _ensure_loaded()
    cfg = NOTIFICATION_REGISTRY.get(event_key)
    if not cfg:
        return None

    key = cfg.get("key") or cfg.get("event_key") or event_key
    label = cfg.get("label") or key.replace(".", " ").replace("_", " ").title()
    enabled = bool(cfg.get("enabled", True))
    if not enabled:
        return None

    roles = list(cfg.get("roles") or [])
    priority = str(cfg.get("priority", "medium"))
    channels = _derive_channels(cfg)
    templates = cfg.get("templates") or {}

    return EventMeta(
        key=key,
        label=label,
        enabled=enabled,
        roles=roles,
        priority=priority,
        channels=channels,
        templates=templates,
        raw=cfg,
    )


def get_all_events(include_disabled: bool = False) -> List[EventMeta]:
    """
    Useful for admin/diagnostics. Builds EventMeta for all registered events.
    """
    _ensure_loaded()
    out: List[EventMeta] = []
    for k, cfg in NOTIFICATION_REGISTRY.items():
        em = get_event(k)
        if em:
            out.append(em)
        elif include_disabled:
            # Return disabled too, marked enabled=False
            key = cfg.get("key") or cfg.get("event_key") or k
            out.append(EventMeta(
                key=key,
                label=cfg.get("label") or key.replace(".", " ").title(),
                enabled=False,
                roles=list(cfg.get("roles") or []),
                priority=str(cfg.get("priority", "medium")),
                channels=_derive_channels(cfg),
                templates=cfg.get("templates") or {},
                raw=cfg,
            ))
    return out