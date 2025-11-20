from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class UnpaidOrderService:
    """
    Service to mark an order as unpaid.

    Methods:
        mark_unpaid: Transitions the order to 'unpaid' status if allowed.
    """

    def mark_unpaid(self, order_id: int) -> Order:
        """
        Mark an order as unpaid.

        Args:
            order_id (int): ID of the order to mark unpaid.

        Returns:
            Order: The updated order instance.

        Raises:
            ValueError: If order cannot be marked unpaid.
        """
        order = get_order_by_id(order_id)

        if order.status not in ('new', 'cancelled'):
            raise ValueError(
                f"Order {order_id} cannot be marked unpaid from status "
                f"{order.status}."
            )

        order.status = 'unpaid'
        save_order(order)
        return order