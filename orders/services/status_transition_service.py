from datetime import datetime
from typing import Optional, Dict, List

from django.core.exceptions import ValidationError

from orders.models import Order
from orders.utils.order_utils import (
    get_orders_by_status_older_than,
    save_order
)
from audit_logging.services.audit_log_service import AuditLogService
from orders.exceptions import (
    InvalidTransitionError,
    AlreadyInTargetStatusError,
)

VALID_TRANSITIONS: Dict[str, List[str]] = {
    # Initial states
    "pending": ["unpaid", "cancelled", "deleted"],
    "created": ["pending", "unpaid", "cancelled"],
    
    # Payment states
    "unpaid": ["paid", "cancelled", "deleted", "on_hold", "pending"],
    "paid": ["available", "pending_writer_assignment", "in_progress", "on_hold", "cancelled"],
    
    # Assignment states
    "pending_writer_assignment": ["available", "cancelled", "on_hold", "in_progress"],
    "available": ["in_progress", "cancelled", "on_hold", "reassigned"],
    
    # Active work states
    "in_progress": ["on_hold", "cancelled", "submitted", "reassigned", "under_editing"],
    "on_hold": ["in_progress", "cancelled", "available", "reassigned"],
    "reassigned": ["in_progress", "available", "on_hold"],
    
    # Submission and review states
    "submitted": ["reviewed", "rated", "revision_requested", "disputed", "cancelled", "under_editing"],
    "reviewed": ["rated", "revision_requested", "approved"],
    "rated": ["approved", "revision_requested", "completed"],
    "approved": ["archived", "completed"],
    "completed": ["approved", "archived", "closed"],
    
    # Revision states
    "revision_requested": ["revision_in_progress", "reassigned", "on_hold", "cancelled"],
    "revision_in_progress": ["revised", "submitted", "cancelled", "reassigned", "closed", "on_hold"],
    "revised": ["reviewed", "rated", "approved", "revision_requested", "cancelled", "closed", "under_editing"],
    "on_revision": ["revised", "revision_in_progress", "cancelled"],
    
    # Editing states
    "under_editing": ["submitted", "in_progress", "revised", "cancelled", "on_hold"],
    
    # Dispute states
    "disputed": ["in_progress", "revision_requested", "cancelled", "closed", "refunded"],
    
    # Final states
    "cancelled": ["reopened", "unpaid", "refunded"],
    "reopened": ["unpaid", "pending", "available"],
    "refunded": ["closed", "cancelled"],
    "archived": ["closed"],
    "closed": [],
    "deleted": [],
}


class StatusTransitionService:
    """
    Handles valid status transitions for orders, both manual and batch.
    """

    def __init__(self, *, user=None):
        """
        Initialize the service.

        Args:
            user (User, optional): The user performing the action.
        """
        self.user = user

    @staticmethod
    def move_complete_orders_to_approved_older_than(
        cutoff_date: datetime
    ) -> None:
        """
        Promote 'complete' orders to 'approved' if older than a given date.

        Args:
            cutoff_date (datetime): Threshold for order promotion.
        """
        orders = get_orders_by_status_older_than("complete", cutoff_date)
        for order in orders:
            order.status = "approved"
            save_order(order)

    @staticmethod
    def reopen_cancelled_order_to_unpaid(
        order_id: int
    ) -> Optional[Order]:
        """
        Restore a cancelled order to 'unpaid' status.
        Useful in instances when the client wants to reprocess a cancelled order.
        Useful when the client does not want to retype everything again
        and just wants to reactivate the order.
        This is typically used in cases where the order was cancelled by mistake
        or needs to be reactivated for some reason.
        This method finds a cancelled order by ID and changes its status to 'unpaid'.
        This is useful for cases where a client wants to reprocess a cancelled order.
        It is important to note that this method does not check if the order is
        actually eligible for reactivation, so it should be used with caution.

        Args:
            order_id (int): ID of the order to update.

        Returns:
            Optional[Order]: The updated order, or None if not found.
        """
        order = Order.objects.filter(
            id=order_id, status="cancelled"
        ).first()
        if not order:
            return None
        order.status = "unpaid"
        order.save(update_fields=["status"])
        return order

    def transition_order_to_status(
        self,
        order: Order,
        target_status: str,
        *,
        metadata: Optional[dict] = None,
        log_action: bool = True,
        skip_payment_check: bool = False,
        reason: Optional[str] = None
    ) -> Order:
        """
        Transition an order to a new status if valid.

        Args:
            order (Order): The order instance.
            target_status (str): The new status to apply.
            metadata (dict, optional): Extra info for audit logging.
            log_action (bool): Whether to log the transition.
            skip_payment_check (bool): Skip payment validation (for admin overrides).
            reason (str, optional): Reason for the transition.

        Returns:
            Order: The updated order instance.

        Raises:
            AlreadyInTargetStatusError: If already in target state.
            InvalidTransitionError: If the transition is not allowed.
            ValidationError: If payment is required but not completed.
        """
        current = order.status

        if target_status == current:
            raise AlreadyInTargetStatusError(
                f"Order is already in status '{target_status}'."
            )

        allowed = VALID_TRANSITIONS.get(current, [])
        if target_status not in allowed:
            raise InvalidTransitionError(
                f"Cannot move from '{current}' to '{target_status}'. "
                f"Allowed transitions: {', '.join(allowed)}"
            )

        # Validate payment requirement for statuses that require payment
        payment_required_statuses = ['in_progress', 'available', 'pending_writer_assignment', 'submitted']
        if not skip_payment_check and target_status in payment_required_statuses:
            self._validate_payment_completed(order, target_status)
        
        # Validate writer assignment for statuses that require it
        writer_required_statuses = ['in_progress', 'submitted', 'revision_in_progress', 'revised']
        if target_status in writer_required_statuses and not order.assigned_writer:
            raise ValidationError(
                f"Cannot transition order to '{target_status}': "
                "Order must have an assigned writer."
            )

        # Perform transition
        order.status = target_status
        save_order(order)

        if log_action and self.user:
            AuditLogService.log_auto(
                actor=self.user,
                action="STATUS_TRANSITION",
                target=order,
                metadata={
                    "old_status": current,
                    "new_status": target_status,
                    "reason": reason,
                    **(metadata or {})
                },
            )

        return order
    
    def get_available_transitions(self, order: Order) -> List[str]:
        """
        Get list of available transitions for an order.
        
        Args:
            order: The order instance
            
        Returns:
            List of available target statuses
        """
        current_status = order.status
        return VALID_TRANSITIONS.get(current_status, [])

    @staticmethod
    def _validate_payment_completed(order: Order, target_status: str) -> None:
        """
        Validate that order has a completed payment before allowing transition.
        
        Args:
            order: The order instance.
            target_status: The target status being transitioned to.
            
        Raises:
            ValidationError: If payment is required but not completed.
        """
        # Check if order has a completed payment
        from django.apps import apps
        OrderPayment = apps.get_model('order_payments_management', 'OrderPayment')
        
        has_completed_payment = OrderPayment.objects.filter(
            order=order,
            status__in=['completed', 'succeeded']
        ).exists()
        
        if not has_completed_payment and not order.is_paid:
            raise ValidationError(
                f"Cannot transition order to '{target_status}': "
                "Order must have a completed payment before moving to this status. "
                "Please complete payment first."
            )