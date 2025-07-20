"""A module to map notification priority labels to
their corresponding enum values and vice versa.
This is useful for ensuring consistent handling
of notification priorities across the system.
"""
import logging
from notifications_system.enums import (
    NotificationPriority
)

logger = logging.getLogger(__name__)

# Label → Priority enum mapping
LABEL_TO_PRIORITY = {
    "emergency": NotificationPriority.EMERGENCY,
    "high": NotificationPriority.HIGH,
    "medium_high": NotificationPriority.MEDIUM_HIGH,
    "normal": NotificationPriority.NORMAL,
    "low": NotificationPriority.LOW,
    "passive": NotificationPriority.PASSIVE,

    # Aliases (optional)
    "urgent": NotificationPriority.HIGH,
    "default": NotificationPriority.NORMAL,
    "background": NotificationPriority.LOW,
    "digest": NotificationPriority.PASSIVE,
}

# Priority enum → label
PRIORITY_TO_LABEL = {
    NotificationPriority.EMERGENCY: "emergency",
    NotificationPriority.HIGH: "high",
    NotificationPriority.MEDIUM_HIGH: "medium_high",
    NotificationPriority.NORMAL: "normal",
    NotificationPriority.LOW: "low",
    NotificationPriority.PASSIVE: "passive",
}

# For DRF ChoiceField / frontend dropdowns
PRIORITY_LABEL_CHOICES = [
    (label, label.replace("_", " ").title())
    for label in PRIORITY_TO_LABEL.values()
]

def get_priority_from_label(label: str) -> int:
    if not isinstance(label, str):
        logger.warning(
            f"Invalid priority label type: {label!r}"
            f" Expected string, got {type(label).__name__}."
        )
        return NotificationPriority.NORMAL

    key = label.strip().lower()
    priority = LABEL_TO_PRIORITY.get(key)

    if priority is None:
        logger.warning(
            f"Unknown priority label '{label}'."
            f" Falling back to NORMAL."
        )
        return NotificationPriority.NORMAL

    return priority

def get_label_from_priority(value: int) -> str:
    return PRIORITY_TO_LABEL.get(
        NotificationPriority(value),
        "normal"
    )
