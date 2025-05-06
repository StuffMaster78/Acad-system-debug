from special_orders.services.order_completion_log_service import (
    OrderCompletionLogService
)
import logging

from special_orders.models import SpecialOrder


logger = logging.getLogger("special_orders")

class CompletionService:
    """
    Handles order completion logic.
    """

    @staticmethod
    def complete_special_order(special_order: SpecialOrder, completed_by, method, justification=""):
        """
        Marks an order as completed and logs the event.

        Args:
            order (SpecialOrder): The order to complete.
            completed_by (User): The user completing the order.
            method (str): Completion method (e.g., 'manual', 'auto').
            justification (str): Optional reason for completion.

        Returns:
            SpecialOrder: The updated order instance.
        """
        if special_order.status != 'completed':
            special_order.status = 'completed'
            special_order.save()
            logger.info(f"Special order #{special_order.id} marked as completed.")
            
            OrderCompletionLogService.log_order_completion(
                special_order, completed_by, method, justification
            )

        return special_order