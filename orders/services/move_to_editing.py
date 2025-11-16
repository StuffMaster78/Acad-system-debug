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
        
        if not should_edit:
            # Skip editing - move directly to reviewed/completed status
            order.editing_skip_reason = reason
            order.status = OrderStatus.REVIEWED.value  # Skip editing, mark as reviewed
            save_order(order)
            
            AuditLogService.log_auto(
                actor=user,
                action="EDIT_SKIP",  # Shortened to fit max_length
                target=order,
                metadata={
                    "status": OrderStatus.REVIEWED.value,
                    "editing_skip_reason": reason,
                    "message": "Order submitted - editing skipped",
                },
            )
            
            return order

        # Order should undergo editing
        order.status = OrderStatus.UNDER_EDITING.value
        order.editing_skip_reason = None  # Clear any previous skip reason
        save_order(order)

        AuditLogService.log_auto(
            actor=user,
            action="MOVE_EDIT",  # Shortened to fit max_length
            target=order,
            metadata={
                "status": OrderStatus.UNDER_EDITING.value,
                "message": "Moved order to under_editing",
            },
        )

        # Auto-assign to editor if possible
        try:
            from editor_management.services.editor_assignment_service import EditorAssignmentService
            EditorAssignmentService.auto_assign_order(order)
        except Exception:
            # If auto-assignment fails, that's okay - task can be manually assigned or claimed
            pass

        return order