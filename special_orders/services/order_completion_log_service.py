from special_orders.models import OrderCompletionLog


class OrderCompletionLogService:
    """
    Service class to manage operations related to OrderCompletionLog.
    """

    @staticmethod
    def log_order_completion(order, user, method, justification=""):
        """
        Creates a completion log entry for a completed order.

        Args:
            order (SpecialOrder): The completed order.
            user (User): The user who completed the order.
            method (str): The method used for completion.
            justification (str): Optional justification text.

        Returns:
            OrderCompletionLog: The created log entry.
        """
        return OrderCompletionLog.objects.create(
            special_order=order,
            completed_by=user,
            completion_method=method,
            justification=justification,
            website=order.website
        )