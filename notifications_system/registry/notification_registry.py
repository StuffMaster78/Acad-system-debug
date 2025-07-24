""""Notification Registry for the Notifications System
This module manages the registration and
retrieval of notification events and their configurations.
It allows for flexible and extensible notification
management based on event keys.
"""
from notifications_system.registry.event_config_loader import (
    get_event_config
)

NOTIFICATION_REGISTRY = {}

def register_notification(force_reload: bool = False, **config):
    config = get_event_config(force_reload=force_reload)
    NOTIFICATION_REGISTRY.clear()
    NOTIFICATION_REGISTRY.update(config)

def get_notification_config(event_key):
    return NOTIFICATION_REGISTRY.get(event_key)

def get_digest_config(event_key):
    config = NOTIFICATION_REGISTRY.get(event_key)
    if config and config.get("digest"):
        return config["digest"]
    return None

def list_all_event_keys():
    return list(NOTIFICATION_REGISTRY.keys())