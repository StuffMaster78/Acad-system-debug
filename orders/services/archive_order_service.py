from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class ArchiveOrderService:
    """
    Service to archive an order.

    Methods:
        archive_order: Moves order from 'approved' to 'archived'.
    """

    def archive_order(self, order_id: int) -> Order:
        """
        Archive an approved order by its ID.

        Args:
            order_id (int): The ID of the order to archive.

        Returns:
            Order: The updated order in 'archived' state.

        Raises:
            ValueError: If the order is not in 'approved' state.
        """
        order = get_order_by_id(order_id)

        if order.status != 'approved':
            raise ValueError(
                f"Order {order_id} cannot be archived from state "
                f"{order.status}."
            )

        order.status = 'archived'
        save_order(order)
        return order