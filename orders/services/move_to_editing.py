"""
Service class to handle transition of an order to 'under_editing' status.
"""

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.utils.order_utils import save_order
from audit_logging.services.audit_log_service import AuditLogService


class MoveOrderToEditingService:
    """
    Moves an order to the 'under_editing' status after writer submission.
    """

    @staticmethod
    def execute(order: Order, user) -> Order:
        """
        Execute the transition to 'under_editing'.

        Args:
            order (Order): The order instance.
            user (User): The user performing the action.

        Returns:
            Order: The updated order instance.

        Raises:
            ValueError: If order is not in a valid status to move to editing.
        """
        if order.status != OrderStatus.SUBMITTED.value:
            raise ValueError(
                f"Order {order.id} must be in 'submitted' status to move to editing."
            )

        order.status = OrderStatus.UNDER_EDITING.value
        save_order(order)

        AuditLogService.log_auto(
            actor=user,
            action="Moved order to under_editing",
            target=order,
            changes={"status": OrderStatus.UNDER_EDITING.value},
        )

        return order