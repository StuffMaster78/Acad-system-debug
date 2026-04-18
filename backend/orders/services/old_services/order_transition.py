from .base_service import OrderService

class OrderTransitionService(OrderService):
    """
    Handles state transitions for orders.
    """
    def set_status(self, new_status):
        """
        Update the order status.

        Args:
            new_status (str): New status value.
        """
        self.order.status = new_status
        self.save()