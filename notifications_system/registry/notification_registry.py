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
