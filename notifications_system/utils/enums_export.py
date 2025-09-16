"""Utility to export notification-related enums as JSON-friendly dicts."""

from __future__ import annotations

import json
from typing import Any, Dict

from notifications_system.enums import (
    NotificationType,
    NotificationCategory,
    NotificationPriority,
    DeliveryStatus,
)


def export_notification_enums() -> Dict[str, Any]:
    """Return all notification enums in a JSON-serializable format.

    Returns:
        Dict with keys: types, priorities, categories, statuses.
    """
    return {
        "types": [t.value for t in NotificationType],
        "priorities": {
            name: member.value for name, member in NotificationPriority.__members__.items()
        },
        "categories": [c.value for c in NotificationCategory],
        "statuses": [s.value for s in DeliveryStatus],
    }


def export_notification_enums_json(indent: int = 2) -> str:
    """Return enums as a formatted JSON string.

    Args:
        indent: Indentation level for pretty-printing.

    Returns:
        JSON string of all enums.
    """
    return json.dumps(export_notification_enums(), indent=indent)