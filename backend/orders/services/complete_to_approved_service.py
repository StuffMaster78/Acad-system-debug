from datetime import datetime, timedelta
from django.utils.timezone import now
from orders.models import Order
from orders.utils.order_utils import save_order


class CompleteToApprovedService:
    """
    Service to move orders from 'complete' to 'approved' status
    after a set grace period (e.g., 3 weeks).
    """

    GRACE_PERIOD_DAYS = 21  # 3 weeks

    def move_complete_to_approved(self, order: Order) -> Order:
        """
        Transition an order from 'complete' to 'approved' if
        it has been complete longer than the grace period.

        Args:
            order (Order): The order instance to check and update.

        Returns:
            Order: The updated order with 'approved' status.

        Raises:
            ValueError: If order is not in 'complete' state or
                        grace period hasn't elapsed.
        """
        if order.status != 'complete':
            raise ValueError(
                f"Order {order.id} must be in 'complete' status "
                f"to move to 'approved'. Current status: {order.status}"
            )

        if not order.completed_at:
            raise ValueError(
                f"Order {order.id} missing 'completed_at' timestamp."
            )

        elapsed = now() - order.completed_at
        if elapsed < timedelta(days=self.GRACE_PERIOD_DAYS):
            raise ValueError(
                f"Order {order.id} has not been complete for "
                f"{self.GRACE_PERIOD_DAYS} days yet."
            )

        order.status = 'approved'
        save_order(order)
        return order