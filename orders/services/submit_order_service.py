from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.move_to_editing import MoveOrderToEditingService
from django.core.exceptions import ObjectDoesNotExist
from fines.services.fine_automation import auto_issue_late_fine
class SubmitOrderService:
    """
    Handles writer order submission and transition to under_editing.
    """

    def execute(self, order_id, user):
        """
        Submit the order and move it to 'under_editing' if eligible.

        Args:
            order_id (int): ID of the order to submit.
            user (User): Writer performing the action.

        Returns:
            Order: The updated order instance.

        Raises:
            ObjectDoesNotExist: If order does not exist.
            ValueError: If submission is invalid.
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ObjectDoesNotExist("Order not found.")

        if order.status != OrderStatus.IN_PROGRESS.value:
            raise ValueError("Order must be in progress to be submitted.")

        from django.utils import timezone
        order.status = OrderStatus.SUBMITTED.value
        order.submitted_at = timezone.now()  # Track submission time for fine calculation
        order.save(update_fields=["status", "submitted_at"])

        # Fire editing transition (checks if editing should occur)
        MoveOrderToEditingService.execute(order=order, user=user)

        # Auto-issue fine if late
        auto_issue_late_fine(order)
        
        return order