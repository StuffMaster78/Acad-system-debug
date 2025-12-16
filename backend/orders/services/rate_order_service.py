from orders.models import Order
from orders.utils.order_utils import get_order_by_id
from orders.services.transition_helper import OrderTransitionHelper


class RateOrderService:
    """
    Service to handle rating of orders.

    Methods:
        rate_order: Assigns a rating to an order.
    """

    def rate_order(self, order_id: int, rating: int, user=None) -> Order:
        """
        Rate an order with a numeric rating.

        Args:
            order_id (int): ID of the order to rate.
            rating (int): Rating value (e.g., 1 to 5).
            user (User, optional): User rating the order (for logging).

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
        OrderTransitionHelper.transition_order(
            order=order,
            target_status='rated',
            user=user,
            reason=f"Order rated {rating}/5",
            action="rate_order",
            is_automatic=False,
            metadata={"rating": rating, "previous_status": order.status}
        )
        order.save(update_fields=["rating"])
        return order