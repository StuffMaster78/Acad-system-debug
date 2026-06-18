from __future__ import annotations

from django.core.exceptions import ValidationError

from orders.models.orders.enums import OrderStatus


class OrderTransitionWorkflow:
    """
    Own legal order status transitions.

    This class does not save models.
    It only answers whether a transition is allowed.
    """

    TRANSITIONS = {
        OrderStatus.CREATED: {
            OrderStatus.PENDING_PAYMENT,
            OrderStatus.UNPAID,
            OrderStatus.CANCELLED,
        },
        OrderStatus.UNPAID: {
            OrderStatus.PENDING_PAYMENT,
            OrderStatus.READY_FOR_STAFFING,
            OrderStatus.CANCELLED,
        },
        OrderStatus.PENDING_PAYMENT: {
            OrderStatus.READY_FOR_STAFFING,
            OrderStatus.CANCELLED,
        },
        OrderStatus.PAID: {
            OrderStatus.READY_FOR_STAFFING,
            OrderStatus.CANCELLED,
        },
        OrderStatus.READY_FOR_STAFFING: {
            OrderStatus.IN_PROGRESS,
            OrderStatus.ON_HOLD,
            OrderStatus.CANCELLED,
            OrderStatus.PENDING_WRITER_ACCEPTANCE,
        },
        OrderStatus.PENDING_WRITER_ACCEPTANCE: {
            OrderStatus.IN_PROGRESS,
            OrderStatus.READY_FOR_STAFFING,
            OrderStatus.CANCELLED,
        },
        OrderStatus.IN_PROGRESS: {
            OrderStatus.QA_REVIEW,
            OrderStatus.UNDER_EDITING,
            OrderStatus.SUBMITTED,
            OrderStatus.ON_HOLD,
            OrderStatus.READY_FOR_STAFFING,
            OrderStatus.DISPUTED,
            OrderStatus.CANCELLED,
            OrderStatus.PENDING_CANCELLATION,
        },
        OrderStatus.ON_HOLD: {
            OrderStatus.READY_FOR_STAFFING,
            OrderStatus.IN_PROGRESS,
            OrderStatus.CANCELLED,
            OrderStatus.PENDING_CANCELLATION,
        },
        OrderStatus.PENDING_CANCELLATION: {
            OrderStatus.CANCELLED,
            OrderStatus.IN_PROGRESS,
            OrderStatus.READY_FOR_STAFFING,
        },
        OrderStatus.QA_REVIEW: {
            OrderStatus.IN_PROGRESS,
            OrderStatus.UNDER_EDITING,
            OrderStatus.SUBMITTED,
            OrderStatus.DISPUTED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.UNDER_EDITING: {
            OrderStatus.IN_PROGRESS,
            OrderStatus.QA_REVIEW,
            OrderStatus.SUBMITTED,
            OrderStatus.REVISION_REQUESTED,
            OrderStatus.ON_HOLD,
            OrderStatus.CANCELLED,
            OrderStatus.PENDING_CANCELLATION,
        },
        OrderStatus.SUBMITTED: {
            OrderStatus.COMPLETED,
            OrderStatus.DISPUTED,
            OrderStatus.IN_PROGRESS,
            OrderStatus.REVISION_REQUESTED,
            OrderStatus.ON_HOLD,
            OrderStatus.CANCELLED,
        },
        OrderStatus.COMPLETED: {
            OrderStatus.ARCHIVED,
            OrderStatus.DISPUTED,
            OrderStatus.IN_PROGRESS,
            OrderStatus.REVISION_REQUESTED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.DISPUTED: {
            OrderStatus.IN_PROGRESS,
            OrderStatus.SUBMITTED,
            OrderStatus.COMPLETED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.REVISION_REQUESTED: {
            OrderStatus.IN_PROGRESS,
            OrderStatus.UNDER_EDITING,
            OrderStatus.SUBMITTED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.CANCELLED: set(),
        OrderStatus.REFUNDED: set(),
        OrderStatus.ARCHIVED: set(),
    }

    TERMINAL_STATUSES = {
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED,
        OrderStatus.ARCHIVED,
    }

    @classmethod
    def ensure_can_transition(
        cls,
        *,
        current_status: str,
        next_status: str,
    ) -> None:
        """
        Raise ValidationError when transition is not legal.
        """
        allowed = cls.TRANSITIONS.get(current_status, set())

        if next_status not in allowed:
            raise ValidationError(
                f"Cannot transition order from {current_status} "
                f"to {next_status}."
            )

    @classmethod
    def can_transition(
        cls,
        *,
        current_status: str,
        next_status: str,
    ) -> bool:
        """
        Return whether transition is legal.
        """
        return next_status in cls.TRANSITIONS.get(current_status, set())

    @classmethod
    def is_terminal(cls, *, status: str) -> bool:
        """
        Return whether status is terminal.
        """
        return status in cls.TERMINAL_STATUSES
