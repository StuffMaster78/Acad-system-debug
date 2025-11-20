from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class ApproveOrderService:
    """
    Service to approve an order after review and rating.

    Methods:
        approve_order: Transitions the order to 'approved' state if eligible.
    """

    def approve_order(self, order_id: int) -> Order:
        """
        Approve an order by its ID.

        Args:
            order_id (int): The ID of the order to approve.

        Returns:
            Order: The updated order in 'approved' state.

        Raises:
            ValueError: If the order cannot be approved due to its state
                        or missing review/rating.
        """
        order = get_order_by_id(order_id)

        if order.status not in ('reviewed', 'rated', 'complete'):
            raise ValueError(
                f"Order {order_id} cannot be approved from state "
                f"{order.status}."
            )

        # Check if review and rating exist
        if not order.review:
            raise ValueError(f"Order {order_id} lacks a review.")

        if not order.rating:
            raise ValueError(f"Order {order_id} lacks a rating.")

        order.status = 'approved'
        save_order(order)
        return order