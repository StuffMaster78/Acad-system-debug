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
    "pending": ["unpaid", "cancelled", "deleted"],
    "unpaid": ["paid", "cancelled", "deleted", "on_hold"],
    "paid": ["available","pending_writer_assignment", "in_progress", "on_hold", "cancelled"],
    "pending_writer_assignment": ["available", "cancelled", "on_hold"],
    "available": ["in_progress", "cancelled", "on_hold"],
    "in_progress": ["on_hold", "cancelled", "submitted", "reassigned"],
    "on_hold": ["in_progress", "cancelled", "available"],
    "submitted": ["reviewed", "rated", "revision_requested", "disputed", "cancelled"],
    "reviewed": ["rated", "revision_requested"],
    "rated": ["approved", "revision_requested"],
    "approved": ["archived"],
    "cancelled": [],
    "revision_requested": ["revision_in_progress", "reassigned"],
    "revision_in_progress": ["revised", "submitted", "cancelled", "reassigned", "closed"],
    "revised": ["reviewed", "rated", "approved", "revision_requested", "cancelled", "closed"],
    "reassigned": ["in_progress"],
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
        skip_payment_check: bool = False
    ) -> Order:
        """
        Transition an order to a new status if valid.

        Args:
            order (Order): The order instance.
            target_status (str): The new status to apply.
            metadata (dict, optional): Extra info for audit logging.
            log_action (bool): Whether to log the transition.
            skip_payment_check (bool): Skip payment validation (for admin overrides).

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
                f"Cannot move from '{current}' to '{target_status}'."
            )

        # Validate payment requirement for statuses that require payment
        if not skip_payment_check and target_status in ['in_progress', 'available', 'pending_writer_assignment']:
            self._validate_payment_completed(order, target_status)

        order.status = target_status
        save_order(order)

        if log_action and self.user:
            AuditLogService.log_auto(
                actor=self.user,
                action="STATUS_TRANSITION",
                target=order,
                metadata={
                    "status": [current, target_status],
                    **(metadata or {})
                },
            )

        return order

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