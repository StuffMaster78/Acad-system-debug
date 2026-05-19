"""
Compatibility service for older order status transition callers.
"""

from __future__ import annotations

from typing import Optional

from orders.models.orders.enums import OrderStatus
from orders.services.order_transition_service import OrderTransitionService
from orders.workflows.order_transition_workflow import OrderTransitionWorkflow


VALID_TRANSITIONS = {
    status.value: [next_status.value for next_status in allowed]
    for status, allowed in OrderTransitionWorkflow.TRANSITIONS.items()
}


class StatusTransitionService:
    """
    Adapter exposing the legacy transition service interface.
    """

    def __init__(self, *, user=None):
        self.user = user

    def transition_order_to_status(
        self,
        order,
        target_status: str,
        *,
        metadata: Optional[dict] = None,
        log_action: bool = True,
        skip_payment_check: bool = False,
        reason: Optional[str] = None,
    ):
        metadata = {
            "reason": reason,
            "log_action": log_action,
            "skip_payment_check": skip_payment_check,
            **(metadata or {}),
        }
        return OrderTransitionService.transition(
            order=order,
            next_status=target_status,
            actor=self.user,
            event_type="status_transition",
            metadata=metadata,
        )

    def get_available_transitions(self, order) -> list[str]:
        return VALID_TRANSITIONS.get(order.status, [])

    @staticmethod
    def move_complete_orders_to_approved_older_than(cutoff_date) -> None:
        from orders.models.orders import Order

        for order in Order.objects.filter(
            status=OrderStatus.COMPLETED,
            updated_at__lt=cutoff_date,
        ):
            OrderTransitionService.transition(
                order=order,
                next_status=OrderStatus.ARCHIVED,
                event_type="auto_archive_completed_order",
            )

    @staticmethod
    def reopen_cancelled_order_to_unpaid(order_id: int):
        from orders.models.orders import Order

        order = Order.objects.filter(
            id=order_id,
            status=OrderStatus.CANCELLED,
        ).first()
        if not order:
            return None

        order.status = OrderStatus.UNPAID
        order.save(update_fields=["status", "updated_at"])
        return order
