from datetime import datetime
from typing import Optional, Dict, List

from django.core.exceptions import ValidationError

from orders.models import Order
from orders.utils.order_utils import (
    get_orders_by_status_older_than,
    save_order
)
from audit_logging.services import log_audit_action
from orders.exceptions import (
    InvalidTransitionError,
    AlreadyInTargetStatusError,
)

VALID_TRANSITIONS: Dict[str, List[str]] = {
    "pending": ["unpaid", "cancelled"],
    "unpaid": ["paid", "cancelled"],
    "paid": ["available","pending_writer_assignment", "in_progress", "cancelled"],
    "pending_writer_assignment": ["available", "cancelled"],
    "available": ["in_progress", "cancelled", "on_hold"],
    "in_progress": ["on_hold", "submitted", "reassigned"],
    "on_hold": ["in_progress", "cancelled", "available"],
    "submitted": ["reviewed", "revision_requested", "disputed", "cancelled"],
    "reviewed": ["rated", "revision_requested"],
    "rated": ["approved", "revision_requested"],
    "approved": ["archived"],
    "cancelled": [],
    "revision_requested": ["revision_in_progress"],
    "revision_in_progress": ["revised"],
    "revised": ["reviewed"],
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
        log_action: bool = True
    ) -> Order:
        """
        Transition an order to a new status if valid.

        Args:
            order (Order): The order instance.
            target_status (str): The new status to apply.
            metadata (dict, optional): Extra info for audit logging.
            log_action (bool): Whether to log the transition.

        Returns:
            Order: The updated order instance.

        Raises:
            AlreadyInTargetStatusError: If already in target state.
            InvalidTransitionError: If the transition is not allowed.
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

        order.status = target_status
        save_order(order)

        if log_action and self.user:
            log_audit_action(
                actor=self.user,
                action="STATUS_TRANSITION",
                target="orders.Order",
                target_id=order.id,
                changes={"status": [current, target_status]},
                metadata=metadata or {},
            )

        return order