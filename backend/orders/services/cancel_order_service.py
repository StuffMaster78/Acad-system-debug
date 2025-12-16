from decimal import Decimal

from django.apps import apps
from django.db import transaction
from orders.order_enums import OrderStatus
from orders.utils.order_utils import get_order_by_id, save_order


class CancelOrderService:
    """
    Service for canceling an order.

    Methods:
        cancel_order: Cancels an order if allowed.
    """

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id: int, reason: str = "") -> None:
        """
        Cancels the order if it's in a cancellable state.

        Args:
            order_id (int): The ID of the order to cancel.
            reason (str): Optional reason for cancellation.

        Raises:
            ValueError: If the order cannot be canceled.
        """
        order = get_order_by_id(order_id)

        # Check if order can be cancelled (convert enum values to strings for comparison)
        non_cancellable_statuses = [
            OrderStatus.CANCELLED.value,
            OrderStatus.COMPLETED.value,
            OrderStatus.RATED.value,
            OrderStatus.REVIEWED.value,
            OrderStatus.APPROVED.value,
            OrderStatus.ARCHIVED.value,
            OrderStatus.UNPAID.value,
            OrderStatus.PENDING.value,
            OrderStatus.REJECTED.value,
            OrderStatus.EXPIRED.value,
            OrderStatus.REFUNDED.value,
        ]
        
        if order.status in non_cancellable_statuses:
            raise ValueError(
                f"Cannot cancel order in status '{order.status}'."
            )

        # Optional: Save reason or audit log
        if hasattr(order, "cancellation_reason"):
            order.cancellation_reason = reason
            order.save(update_fields=["cancellation_reason"])

        # Use unified transition helper to move to cancelled
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            order,
            OrderStatus.CANCELLED.value,
            user=None,  # System action or pass user if available
            reason=reason or "Order cancelled",
            action="cancel_order",
            is_automatic=False,
            metadata={
                "cancellation_reason": reason,
            }
        )