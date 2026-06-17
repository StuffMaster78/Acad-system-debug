from __future__ import annotations

from typing import Dict, Set

from django.core.exceptions import ValidationError


ALLOWED_PRIMARY_STATUS_TRANSITIONS: Dict[str, Set[str]] = {
    "ready_for_staffing": {
        "in_progress",
        "on_hold",
        "cancelled",
        "pending_writer_acceptance",
    },
    "pending_writer_acceptance": {
        "in_progress",
        "ready_for_staffing",
        "cancelled",
    },
    "in_progress": {
        "submitted",
        "on_hold",
        "ready_for_staffing",
        "cancelled",
        "pending_cancellation",
    },
    "on_hold": {
        "in_progress",
        "ready_for_staffing",
        "cancelled",
        "pending_cancellation",
    },
    "pending_cancellation": {"cancelled", "in_progress", "ready_for_staffing"},
    "submitted": {"completed", "in_progress", "on_hold", "cancelled"},
    "completed": {"in_progress", "archived", "cancelled"},
    "cancelled": set(),
    "archived": set(),
}


def validate_status_transition(
    *,
    from_status: str,
    to_status: str,
) -> None:
    allowed = ALLOWED_PRIMARY_STATUS_TRANSITIONS.get(from_status, set())

    if to_status not in allowed:
        raise ValidationError(
            f"Invalid status transition: {from_status} -> {to_status}"
        )


def can_transition(
    *,
    from_status: str,
    to_status: str,
) -> bool:
    return to_status in ALLOWED_PRIMARY_STATUS_TRANSITIONS.get(
        from_status,
        set(),
    )