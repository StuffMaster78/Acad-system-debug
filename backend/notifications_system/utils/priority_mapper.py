"""Priority mapping utilities for notifications.

Maps between human-readable priority labels (e.g., "high", "urgent")
and the internal ``NotificationPriority`` enum. Ensures consistent
round-trip conversion, even when aliases are used.
"""

import logging
from notifications_system.enums import NotificationPriority

logger = logging.getLogger(__name__)

# Canonical mapping: label → enum
LABEL_TO_PRIORITY = {
    "emergency": NotificationPriority.EMERGENCY,
    "high": NotificationPriority.HIGH,
    "medium_high": NotificationPriority.MEDIUM_HIGH,
    "normal": NotificationPriority.NORMAL,
    "low": NotificationPriority.LOW,
    "passive": NotificationPriority.PASSIVE,
    # Aliases
    "urgent": NotificationPriority.HIGH,
    "default": NotificationPriority.NORMAL,
    "background": NotificationPriority.LOW,
    "digest": NotificationPriority.PASSIVE,
}

# Enum → canonical label
PRIORITY_TO_LABEL = {
    NotificationPriority.EMERGENCY: "emergency",
    NotificationPriority.HIGH: "high",
    NotificationPriority.MEDIUM_HIGH: "medium_high",
    NotificationPriority.NORMAL: "normal",
    NotificationPriority.LOW: "low",
    NotificationPriority.PASSIVE: "passive",
}

# Normalize aliases → canonical
ALIAS_NORMALIZATION = {
    "urgent": "high",
    "default": "normal",
    "background": "low",
    "digest": "passive",
}

# For DRF ChoiceField / frontend dropdowns
PRIORITY_LABEL_CHOICES = [
    (label, label.replace("_", " ").title())
    for label in PRIORITY_TO_LABEL.values()
]


def get_priority_from_label(label: str) -> int:
    """Convert a string label (or alias) into a NotificationPriority enum.

    Args:
        label: Human-readable label, e.g. "urgent", "high", "normal".

    Returns:
        int: Enum value corresponding to the priority.
    """
    if not isinstance(label, str):
        logger.warning(
            "Invalid priority label type: %r (expected str, got %s).",
            label,
            type(label).__name__,
        )
        return NotificationPriority.NORMAL

    key = label.strip().lower()
    priority = LABEL_TO_PRIORITY.get(key)

    if priority is None:
        logger.warning("Unknown priority label '%s'. Falling back to NORMAL.", label)
        return NotificationPriority.NORMAL

    return priority


def get_label_from_priority(value: int, original_label: str | None = None) -> str:
    """Convert a NotificationPriority enum value into its canonical label.

    Args:
        value: Enum integer value.
        original_label: Optional original label string. If it was an alias,
            this will be normalized to its canonical form.

    Returns:
        str: Canonical label, defaults to "normal" if unmapped.
    """
    canonical = PRIORITY_TO_LABEL.get(NotificationPriority(value), "normal")

    if original_label:
        alias = original_label.strip().lower()
        return ALIAS_NORMALIZATION.get(alias, canonical)

    return canonical