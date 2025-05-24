from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class RateOrderService:
    """
    Service to handle rating of orders.

    Methods:
        rate_order: Assigns a rating to an order.
    """

    def rate_order(self, order_id: int, rating: int) -> Order:
        """
        Rate an order with a numeric rating.

        Args:
            order_id (int): ID of the order to rate.
            rating (int): Rating value (e.g., 1 to 5).

        Returns:
            Order: The order instance with updated rating.

        Raises:
            ValueError: If rating is invalid or order not completed.
        """
        order = get_order_by_id(order_id)

        if order.status != 'reviewed':
            raise ValueError(
                f"Order {order_id} can only be rated after review, "
                f"current status {order.status}."
            )

        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5.")

        order.rating = rating
        order.status = 'rated'
        save_order(order)
        return order