"""
Service class to handle transition of an order to 'under_editing' status.
"""

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.utils.order_utils import save_order
from audit_logging.services.audit_log_service import AuditLogService
from editor_management.services.editing_decision_service import EditingDecisionService


class MoveOrderToEditingService:
    """
    Moves an order to the 'under_editing' status after writer submission.
    Uses EditingDecisionService to determine if editing should occur.
    """

    @staticmethod
    def execute(order: Order, user) -> Order:
        """
        Execute the transition to 'under_editing' if order should undergo editing.

        Args:
            order (Order): The order instance.
            user (User): The user performing the action.

        Returns:
            Order: The updated order instance (may skip editing if urgent/disabled).

        Raises:
            ValueError: If order is not in a valid status to move to editing.
        """
        if order.status != OrderStatus.SUBMITTED.value:
            raise ValueError(
                f"Order {order.id} must be in 'submitted' status to move to editing."
            )

        # Check if order should undergo editing
        should_edit, reason = EditingDecisionService.should_undergo_editing(order)
        
        from orders.services.transition_helper import OrderTransitionHelper
        
        if not should_edit:
            # Skip editing - move directly to reviewed/completed status
            order.editing_skip_reason = reason
            OrderTransitionHelper.transition_order(
                order=order,
                target_status=OrderStatus.REVIEWED.value,
                user=user,
                reason=f"Editing skipped: {reason}",
                action="skip_editing",
                is_automatic=True,
                metadata={
                    "editing_skip_reason": reason,
                    "message": "Order submitted - editing skipped",
                }
            )
            order.save(update_fields=["editing_skip_reason"])
            return order

        # Order should undergo editing
        order.editing_skip_reason = None  # Clear any previous skip reason
        OrderTransitionHelper.transition_order(
            order=order,
            target_status=OrderStatus.UNDER_EDITING.value,
            user=user,
            reason="Order moved to editing after submission",
            action="move_to_editing",
            is_automatic=True,
            metadata={
                "message": "Moved order to under_editing",
            }
        )
        order.save(update_fields=["editing_skip_reason"])

        # Auto-assign to editor if possible
        try:
            from editor_management.services.editor_assignment_service import EditorAssignmentService
            EditorAssignmentService.auto_assign_order(order)
        except Exception:
            # If auto-assignment fails, that's okay - task can be manually assigned or claimed
            pass

        return order