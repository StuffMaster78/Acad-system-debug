from orders.models import Order
from orders.utils.order_utils import get_order_by_id
from orders.services.transition_helper import OrderTransitionHelper


class ArchiveOrderService:
    """
    Service to archive an order.

    Methods:
        archive_order: Moves order from 'approved' to 'archived'.
    """

    def archive_order(self, order_id: int, user=None) -> Order:
        """
        Archive an approved order by its ID.

        Args:
            order_id (int): The ID of the order to archive.
            user (User, optional): User performing the archiving (for logging).

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

        OrderTransitionHelper.transition_order(
            order=order,
            target_status='archived',
            user=user,
            reason="Order archived",
            action="archive_order",
            is_automatic=False,
            metadata={"previous_status": order.status}
        )
        return order