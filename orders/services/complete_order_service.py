from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class CompleteOrderService:
    """
    Service to handle marking orders as completed.

    Methods:
        complete_order: Marks the specified order as completed.
    """

    def complete_order(self, order_id: int) -> Order:
        """
        Complete an order by its ID.

        Args:
            order_id (int): The ID of the order to complete.

        Returns:
            Order: The updated order instance marked as completed.

        Raises:
            ValueError: If the order cannot be completed due to state.
        """
        order = get_order_by_id(order_id)

        if order.status != 'processing':
            raise ValueError(
                f"Order {order_id} cannot be completed from state "
                f"{order.status}."
            )

        order.status = 'completed'
        save_order(order)
        return order