from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order
from datetime import datetime, timedelta
from order_configs.models import CriticalDeadlineSetting
from orders.order_enums import OrderStatus

class MarkCriticalOrderService:
    """
    Service to mark an order as critical.

    Methods:
        mark_critical: Marks the order as critical.
    """

    def mark_critical(self, order_id: int) -> Order:
        """
        Mark order as critical.

        Args:
            order_id (int): ID of the order.

        Returns:
            Order: The critical order instance.

        Raises:
            ValueError: If order is already critical.
        """
        order = get_order_by_id(order_id)

        if order.is_critical:
            raise ValueError(f"Order {order_id} is already critical.")

        order.is_critical = True
        save_order(order)
        return order
    

    @staticmethod
    def get_critical_threshold():
        # Grab the first config or default to 24 if none exists
        config = CriticalDeadlineSetting.objects.first()
        if config:
            return config.critical_deadline_threshold_hours
        return 8  # hard fallback

    @staticmethod
    def update_order_status_based_on_deadline(order):
        """Label order CRITICAL if deadline is within threshold hours."""
        if not order.deadline:
            return
        
        threshold_hours = MarkCriticalOrderService.get_critical_threshold()
        now = datetime.utcnow()
        time_left = order.deadline - now
        
        if time_left <= timedelta(hours=threshold_hours):
            if order.status != OrderStatus.CRITICAL:
                order.status = OrderStatus.CRITICAL
                order.save(update_fields=["status"])
        else:
            if order.status == OrderStatus.CRITICAL:
                order.status = OrderStatus.PENDING  # or appropriate fallback
                order.save(update_fields=["status"])