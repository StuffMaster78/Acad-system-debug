from datetime import datetime
from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class ReopenOrderService:
    """
    Service to handle reopening of orders from terminal states like
    'cancelled', 'archived', or 'completed'.

    Methods:
        reopen_order: Transitions an order back to an active state
                      if reopening is allowed.
    """

    def reopen_order(self, order_id: int, reopen_reason: str = None) -> Order:
        """
        Reopen a terminal order and transition it to an active state.

        Args:
            order_id (int): The ID of the order to reopen.
            reopen_reason (str, optional): Reason for reopening.

        Returns:
            Order: The updated order instance.

        Raises:
            ValueError: If the order cannot be reopened.
        """
        order = get_order_by_id(order_id)

        if not order:
            raise ValueError(f"Order {order_id} not found.")

        if order.status not in ('cancelled', 'archived', 'completed'):
            raise ValueError(
                f"Order {order.id} is in status '{order.status}' and cannot "
                "be reopened."
            )

        original_status = order.status

        if original_status == 'archived':
            order.status = 'in_progress'
        elif original_status == 'cancelled':
            order.status = 'unpaid'
        elif original_status == 'completed':
            order.status = 'in_progress'

        order.reopened_from = original_status
        order.reopened_at = datetime.utcnow()
        order.reopen_reason = reopen_reason

        save_order(order)
        return order