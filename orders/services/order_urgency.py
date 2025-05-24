from .base_service import OrderService
from django.utils import timezone


class OrderUrgencyService(OrderService):
    """
    Handles urgency and critical status of orders based on deadlines.
    """

    def is_critical(self, threshold_hours):
        """
        Check if order is critical based on deadline threshold.

        Args:
            threshold_hours (int): Hours before deadline to mark critical.

        Returns:
            bool: True if critical, else False.
        """
        now = timezone.now()
        deadline = self.order.deadline

        if not deadline:
            return False

        delta_hours = (deadline - now).total_seconds() / 3600
        return delta_hours < threshold_hours

    def update_critical_status(self, threshold_hours):
        """
        Update order's critical flag based on threshold.

        Args:
            threshold_hours (int): Hours before deadline to mark critical.
        """
        self.order.is_critical = self.is_critical(threshold_hours)
        self.save()