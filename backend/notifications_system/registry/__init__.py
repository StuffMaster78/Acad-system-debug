"""
Notifications System Registry Package

This package provides centralized registration and retrieval of notification
events and their configurations.
"""

from notifications_system.registry.notification_registry import (
    get_digest_config,
    get_notification_config,
    get_event,
    get_all_events,
    list_all_event_keys,
    list_all_event_configs,
    register_notification,
    bulk_register_notifications,
    EventMeta,
)

__all__ = [
    'get_digest_config',
    'get_notification_config',
    'get_event',
    'get_all_events',
    'list_all_event_keys',
    'list_all_event_configs',
    'register_notification',
    'bulk_register_notifications',
    'EventMeta',
]

