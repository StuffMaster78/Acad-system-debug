# notifications_system/registry/digest_events.py
from __future__ import annotations

"""
Digestable events registry.

Defines events that should be batched (digested) and helpers to query
their config. Keep keys lowercase dotted paths; values are:
    {"delay_minutes": int, "group_by": "<field.path>"}
"""

from typing import Dict, Optional, Tuple, List

# Canonical map of digestable events.
DIGESTABLE_EVENTS: Dict[str, Dict[str, object]] = {
    "order.created": {"delay_minutes": 60, "group_by": "user.id"},
    "order.revision.created": {"delay_minutes": 30, "group_by": "user.id"},
    "order.completed": {"delay_minutes": 120, "group_by": "user.id"},
    "user.signup": {"delay_minutes": 30, "group_by": "user.id"},
    "user.profile_updated": {"delay_minutes": 15, "group_by": "user.id"},
    "user.password_reset": {"delay_minutes": 45, "group_by": "user.id"},
    "user.login": {"delay_minutes": 10, "group_by": "user.id"},
    "user.logout": {"delay_minutes": 10, "group_by": "user.id"},
    "comment.replied": {"delay_minutes": 30, "group_by": "user.id"},
    "comment.liked": {"delay_minutes": 20, "group_by": "user.id"},
    "comment.reported": {"delay_minutes": 60, "group_by": "user.id"},
    "post.created": {"delay_minutes": 60, "group_by": "user.id"},
    "post.updated": {"delay_minutes": 30, "group_by": "user.id"},
    "post.deleted": {"delay_minutes": 120, "group_by": "user.id"},
    "notification.received": {"delay_minutes": 15, "group_by": "user.id"},
    "notification.read": {"delay_minutes": 10, "group_by": "user.id"},
    "notification.acknowledged": {
        "delay_minutes": 20,
        "group_by": "user.id",
    },
    "comment.added": {"delay_minutes": 45, "group_by": "user.id"},
    "post.published": {"delay_minutes": 90, "group_by": "user.id"},
    "notification.sent": {"delay_minutes": 30, "group_by": "user.id"},
    "system.alert": {"delay_minutes": 120, "group_by": "system.id"},
    "task.completed": {"delay_minutes": 60, "group_by": "task.id"},
    "event.reminder": {"delay_minutes": 15, "group_by": "event.id"},
    "feedback.received": {"delay_minutes": 30, "group_by": "user.id"},
    "subscription.renewed": {"delay_minutes": 60, "group_by": "user.id"},
    "payment.failed": {"delay_minutes": 120, "group_by": "user.id"},
    "payment.success": {"delay_minutes": 60, "group_by": "user.id"},
    "alert.critical": {"delay_minutes": 30, "group_by": "alert.id"},
    # “digest.*” keys below allow category-based batching if you emit them
    "digest.notification": {"delay_minutes": 60, "group_by": "user.id"},
    "digest.event": {"delay_minutes": 60, "group_by": "user.id"},
    "digest.system": {"delay_minutes": 120, "group_by": "system.id"},
    "digest.task": {"delay_minutes": 60, "group_by": "task.id"},
    "digest.feedback": {"delay_minutes": 30, "group_by": "user.id"},
    "digest.subscription": {"delay_minutes": 60, "group_by": "user.id"},
    "digest.payment": {"delay_minutes": 120, "group_by": "user.id"},
    "digest.alert": {"delay_minutes": 30, "group_by": "alert.id"},
}

# --------------------
# Query helpers
# --------------------

def get_digestable_events() -> Dict[str, Dict[str, object]]:
    """Return the digestable events mapping."""
    return DIGESTABLE_EVENTS


def is_digestable(event_key: str) -> bool:
    """Return True if the event is configured for digest."""
    return event_key in DIGESTABLE_EVENTS


def get_digest_config(event_key: str) -> Dict[str, object]:
    """Return the digest config for an event or {} if not present."""
    return DIGESTABLE_EVENTS.get(event_key, {})


def get_digest_delay(event_key: str) -> Optional[int]:
    """Return delay (minutes) for an event, or None if not digestable."""
    cfg = get_digest_config(event_key)
    return int(cfg["delay_minutes"]) if "delay_minutes" in cfg else None


def get_digest_group_by(event_key: str) -> Optional[str]:
    """Return group_by key for an event, or None if not digestable."""
    cfg = get_digest_config(event_key)
    return str(cfg["group_by"]) if "group_by" in cfg else None


def list_digestable_event_keys() -> List[str]:
    """Return a list of digestable event keys."""
    return list(DIGESTABLE_EVENTS.keys())

# --------------------
# Validation helpers
# --------------------

def validate_digest_config() -> List[Tuple[str, str]]:
    """Validate the digest registry.

    Checks each event has:
      * integer 'delay_minutes' >= 0
      * non-empty 'group_by' string

    Returns:
        List of (event_key, error_message) tuples. Empty means OK.
    """
    errors: List[Tuple[str, str]] = []
    for key, cfg in DIGESTABLE_EVENTS.items():
        if "delay_minutes" not in cfg:
            errors.append((key, "missing delay_minutes"))
        else:
            try:
                if int(cfg["delay_minutes"]) < 0:
                    errors.append((key, "delay_minutes < 0"))
            except Exception:
                errors.append((key, "delay_minutes not int-like"))

        gb = cfg.get("group_by")
        if not isinstance(gb, str) or not gb.strip():
            errors.append((key, "invalid group_by"))
    return errors