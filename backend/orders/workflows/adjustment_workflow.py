from __future__ import annotations

from django.core.exceptions import ValidationError

from orders.models.orders.enums import (
    OrderAdjustmentStatus,
)


class AdjustmentWorkflow:
    """
    Workflow manager for order adjustments.
    Owns legal status transitions for order adjustments
    and encapsulates related business logic.

    Services should call this before updating the status of an
    order adjustment request to ensure valid state transitions
    and trigger necessary side effects.
    """

    TRANSITIONS = {
        OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE: {
            OrderAdjustmentStatus.CLIENT_COUNTERED,
            OrderAdjustmentStatus.ACCEPTED,
            OrderAdjustmentStatus.DECLINED,
            OrderAdjustmentStatus.EXPIRED,
            OrderAdjustmentStatus.CANCELLED,
        },
        OrderAdjustmentStatus.CLIENT_COUNTERED: {
            OrderAdjustmentStatus.FUNDING_PENDING,
            OrderAdjustmentStatus.DECLINED,
            OrderAdjustmentStatus.CANCELLED,
        },
        OrderAdjustmentStatus.ACCEPTED: {
            OrderAdjustmentStatus.FUNDING_PENDING,
            OrderAdjustmentStatus.CANCELLED,
        },
        OrderAdjustmentStatus.FUNDING_PENDING: {
            OrderAdjustmentStatus.FUNDED,
            OrderAdjustmentStatus.COUNTER_FUNDED_FINAL,
            OrderAdjustmentStatus.CANCELLED,
            OrderAdjustmentStatus.EXPIRED,
        },
        OrderAdjustmentStatus.FUNDED: {
            OrderAdjustmentStatus.REVERSED,
        },
        OrderAdjustmentStatus.COUNTER_FUNDED_FINAL: {
            OrderAdjustmentStatus.REVERSED,
            OrderAdjustmentStatus.APPROVED_BY_STAFF,
        },

    }


    TERMINAL_STATUSES = {
        OrderAdjustmentStatus.DECLINED,
        OrderAdjustmentStatus.EXPIRED,
        OrderAdjustmentStatus.CANCELLED,
        OrderAdjustmentStatus.REVERSED,
        OrderAdjustmentStatus.REJECTED_BY_CLIENT,
        OrderAdjustmentStatus.REJECTED_BY_STAFF,
    }


    @classmethod
    def ensure_can_transition(
        cls, *, current_status: str, next_status: str
    ) -> None:
        """
        Validates that an order adjustment can transition from current_status to next_status.
        Raises ValidationError if the transition is not allowed.
        """
        try:
            current = OrderAdjustmentStatus(current_status)
            next_ = OrderAdjustmentStatus(next_status)
        except ValueError:
            raise ValidationError(
                f"Invalid adjustment status value(s): '{current_status}', '{next_status}'."
            )

        if current == next_:
            raise ValidationError(f"Adjustment is already in status {current_status}.")

        allowed_transitions = cls.TRANSITIONS.get(current, set())
        if next_ not in allowed_transitions:
            raise ValidationError(
                f"Invalid status! Cannot transition adjustment from {current_status} to {next_status}."
            )
    @classmethod
    def is_terminal_status(cls, status: str) -> bool:
        """
        Checks if a given status is a terminal status.

        Args:
            status (str): The status to check.

        Returns:
            bool: True if the status is terminal, False otherwise.
        """
        try:
            return OrderAdjustmentStatus(status) in cls.TERMINAL_STATUSES
        except ValueError:
            return False