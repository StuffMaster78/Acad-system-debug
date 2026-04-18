from __future__ import annotations

from dataclasses import dataclass

from django.utils import timezone

from orders.models.orders import Order
from orders.models.orders.constants import (
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_ON_HOLD,
    ORDER_STATUS_SUBMITTED,
)


@dataclass(frozen=True)
class OrderOperationalState:
    """
    Represent derived operational monitoring state for an order.
    """

    is_late: bool
    is_critical: bool
    seconds_to_writer_deadline: int | None
    state_label: str


class OrderMonitoringService:
    """
    Own derived operational monitoring logic for orders.

    Responsibilities:
        1. Determine whether an order is late.
        2. Determine whether an order is critical.
        3. Provide remaining time to the writer deadline.
        4. Produce a compact derived operational state.

    These are derived operational states, not lifecycle statuses.
    """

    CRITICAL_THRESHOLD_SECONDS = 3 * 60 * 60

    ACTIVE_EXECUTION_STATUSES = frozenset(
        {
            ORDER_STATUS_IN_PROGRESS,
            ORDER_STATUS_ON_HOLD,
            ORDER_STATUS_SUBMITTED,
        }
    )

    @classmethod
    def build_operational_state(
        cls,
        *,
        order: Order,
    ) -> OrderOperationalState:
        """
        Build a derived operational state for an order.

        Args:
            order:
                Order being evaluated.

        Returns:
            OrderOperationalState:
                Derived monitoring state.
        """
        seconds_to_deadline = cls.seconds_to_writer_deadline(order=order)
        is_late = cls.is_order_late(order=order)
        is_critical = cls.is_order_critical(order=order)

        if is_late:
            state_label = "late"
        elif is_critical:
            state_label = "critical"
        else:
            state_label = "normal"

        return OrderOperationalState(
            is_late=is_late,
            is_critical=is_critical,
            seconds_to_writer_deadline=seconds_to_deadline,
            state_label=state_label,
        )

    @classmethod
    def is_order_late(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the order has crossed the writer deadline.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when the writer deadline has passed.
        """
        writer_deadline = getattr(order, "writer_deadline", None)
        if writer_deadline is None:
            return False

        if order.status not in cls.ACTIVE_EXECUTION_STATUSES:
            return False

        return timezone.now() > writer_deadline

    @classmethod
    def is_order_critical(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the order is nearing the writer deadline.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when the deadline is near but not yet late.
        """
        seconds_remaining = cls.seconds_to_writer_deadline(order=order)
        if seconds_remaining is None:
            return False

        if order.status not in cls.ACTIVE_EXECUTION_STATUSES:
            return False

        return 0 <= seconds_remaining <= cls.CRITICAL_THRESHOLD_SECONDS

    @staticmethod
    def seconds_to_writer_deadline(
        *,
        order: Order,
    ) -> int | None:
        """
        Return remaining seconds until the writer deadline.

        Args:
            order:
                Order being evaluated.

        Returns:
            int | None:
                Remaining seconds, or None when no writer deadline exists.
        """
        writer_deadline = getattr(order, "writer_deadline", None)
        if writer_deadline is None:
            return None

        delta = writer_deadline - timezone.now()
        return int(delta.total_seconds())