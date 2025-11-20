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

        if order.status in [
            OrderStatus.CANCELLED,
            OrderStatus.COMPLETED,
            OrderStatus.RATED,
            OrderStatus.REVIEWED,
            OrderStatus.APPROVED,
            OrderStatus.ARCHIVED,
            OrderStatus.UNPAID,
            OrderStatus.PENDING,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
            OrderStatus.FAILED,
            OrderStatus.REFUNDED,
            OrderStatus.PARTIALLY_REFUNDED
        ]:
            raise ValueError(
                f"Cannot cancel order in status '{order.status.value}'."
            )

        order.status = OrderStatus.CANCELLED

        # Optional: Save reason or audit log
        if hasattr(order, "cancellation_reason"):
            order.cancellation_reason = reason

        # Optional: Refunds or cleanup hooks can go here

        save_order(order)