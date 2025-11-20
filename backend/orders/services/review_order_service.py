from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class ReviewOrderService:
    """
    Service to handle review submission for an order.

    Methods:
        submit_review: Adds a review comment to the given order.
    """

    def submit_review(self, order_id: int, review: str) -> Order:
        """
        Submit a review for an order by its ID.

        Args:
            order_id (int): The ID of the order to review.
            review (str): The review text.

        Returns:
            Order: The updated order with the review saved.

        Raises:
            ValueError: If the order is not eligible for review or the
                        review is empty.
        """
        order = get_order_by_id(order_id)

        if order.status != 'complete':
            raise ValueError(
                f"Order {order_id} cannot be reviewed from state "
                f"{order.status}."
            )

        if not review or not review.strip():
            raise ValueError("Review text cannot be empty.")

        order.review = review.strip()
        save_order(order)
        return order