"""
orders/services/order_hold_service.py

Service class to handle putting orders on hold and resuming them.
"""

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.utils.order_utils import save_order


class HoldOrderService:
    """
    Service to manage holding and resuming orders.

    Args:
        order (Order): The order instance to modify.
        user: The user performing the action.

    Methods:
        put_on_hold(): Puts the order on hold if allowed.
        resume(): Resumes the order if it is currently on hold.
    """
    def __init__(self, order: Order, user):
        self.order = order
        self.user = user

    def put_on_hold(self):
        """
        Put an order on hold if its status allows it.

        Args:
            order (Order): The order instance to put on hold.
            user (User): The user performing the action.

        Raises:
            ValueError: If order status does not allow hold.

        Returns:
            Order: Updated order instance.
        """
        if self.order.status not in {
            OrderStatus.PENDING,
            OrderStatus.IN_PROGRESS,
        }:
            raise ValueError("Order cannot be put on hold from current status.")

        self.order.status = OrderStatus.ON_HOLD
        save_order(self.order, user=self.user, event="order_put_on_hold")
        return self.order

    def resume(self):
        """
        Resume an order that is currently on hold.

        Args:
            order (Order): The order instance to resume.
            user (User): The user performing the action.

        Raises:
            ValueError: If order is not on hold.

        Returns:
            Order: Updated order instance.
        """
        if self.order.status != OrderStatus.ON_HOLD:
            raise ValueError("Only ON_HOLD orders can be resumed.")

        self.order.status = OrderStatus.IN_PROGRESS
        save_order(self.order, user=self.user, event="order_resumed")
        return self.order