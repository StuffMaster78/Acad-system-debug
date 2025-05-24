from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class MarkLateOrderService:
    """
    Service to mark orders as late.

    Methods:
        mark_late: Marks an order as late.
    """

    def mark_late(self, order_id: int) -> Order:
        """
        Mark the order as late.

        Args:
            order_id (int): ID of the order.

        Returns:
            Order: The order marked as late.

        Raises:
            ValueError: If order is already late or completed.
        """
        order = get_order_by_id(order_id)

        if order.status in ('completed', 'cancelled'):
            raise ValueError(
                f"Cannot mark order {order_id} late from status "
                f"{order.status}."
            )

        order.is_late = True
        save_order(order)
        return order