from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class MarkOrderPaidService:
    """
    Service to mark an order as paid.

    Methods:
        mark_paid: Transitions the order to 'in_progress' if allowed.
    """

    def mark_paid(self, order_id: int) -> Order:
        """
        Mark an order as paid and move to in_progress.

        Args:
            order_id (int): ID of the order to mark as paid.

        Returns:
            Order: The updated order instance.

        Raises:
            ValueError: If the order cannot be marked as paid.
        """
        order = get_order_by_id(order_id)

        if order.status != 'unpaid':
            raise ValueError(
                f"Order {order_id} cannot be marked paid from status "
                f"{order.status}."
            )

        order.status = 'in_progress'
        save_order(order)
        return order