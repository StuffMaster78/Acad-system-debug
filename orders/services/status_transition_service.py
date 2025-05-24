from datetime import datetime
from typing import Optional

from orders.models import Order
from orders.utils.order_utils import get_orders_by_status_older_than, save_order


class StatusTransitionService:
    """
    Handles state transitions between orders, including reopening and
    moving orders based on time thresholds.
    """

    @staticmethod
    def move_complete_orders_to_approved_older_than(cutoff_date: datetime) -> None:
        """
        Move orders from 'complete' to 'approved' if older than cutoff_date.

        Args:
            cutoff_date (datetime): The date before which orders are moved.
        """
        orders = get_orders_by_status_older_than('complete', cutoff_date)
        for order in orders:
            order.status = 'approved'
            save_order(order)

    @staticmethod
    def reopen_cancelled_order_to_unpaid(order_id: int) -> Optional[Order]:
        """
        Reopen a cancelled order by moving it to 'unpaid'.

        Args:
            order_id (int): The ID of the order to reopen.

        Returns:
            Order or None: The updated order or None if invalid.
        """
        order = Order.objects.filter(id=order_id, status='cancelled').first()
        if not order:
            return None
        order.status = 'unpaid'
        save_order(order)
        return order

    # Add more transition methods as your flow demands