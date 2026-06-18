from __future__ import annotations

from django.core.exceptions import ValidationError

from orders.workflows.order_transition_workflow import (
    OrderTransitionWorkflow,
)

ALLOWED_PRIMARY_STATUS_TRANSITIONS: dict[str, set[str]] = {
    status.value: {next_status.value for next_status in allowed}
    for status, allowed in OrderTransitionWorkflow.TRANSITIONS.items()
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
