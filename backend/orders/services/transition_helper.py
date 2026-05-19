"""
Compatibility helper for older order status transition callers.
"""

from __future__ import annotations

from orders.services.status_transition_service import StatusTransitionService
from orders.services.status_transition_service import VALID_TRANSITIONS


class OrderTransitionHelper:
    """
    Adapter exposing the legacy helper interface.
    """

    @staticmethod
    def can_transition(order, target_status: str) -> bool:
        return target_status in VALID_TRANSITIONS.get(order.status, [])

    @staticmethod
    def get_available_transitions(order) -> list[str]:
        return VALID_TRANSITIONS.get(order.status, [])

    @staticmethod
    def transition_order(
        order,
        target_status: str,
        user=None,
        reason=None,
        metadata=None,
        **kwargs,
    ):
        service = StatusTransitionService(user=user)
        return service.transition_order_to_status(
            order,
            target_status,
            reason=reason,
            metadata=metadata,
            skip_payment_check=kwargs.get("skip_payment_check", False),
        )

    @staticmethod
    def register_before_hook(*args, **kwargs) -> None:
        return None

    @staticmethod
    def register_after_hook(*args, **kwargs) -> None:
        return None
