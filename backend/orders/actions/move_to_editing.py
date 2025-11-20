from orders.actions.base import BaseOrderAction
from orders.services.move_to_editing import MoveOrderToEditingService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("move_to_editing")
class MoveOrderToEditingAction(BaseOrderAction):
    """
    Action to transition an order to 'under_editing' status.
    When an order is moved to editing, it indicates that the order is being processed
    by the editor. This is typically used for manual operations,
    like an admin action to indicate that the order is currently being edited.
    This action logs an audit trail for the transition.
    Attributes:
        order (Order): The order instance to be transitioned.
        user (User): The user performing the action.
        action_name (str): The name of the action, default is "move_to_editing".
    This action is registered in the order action registry.
    It is typically used when an order needs to be moved to an editing state,
    such as when an admin or user needs to make changes to the order details.
    """

    def execute(self):
        """
        Executes the editing transition and logs the audit trail.

        Returns:
            Order: The updated order instance.

        Raises:
            ValueError: If transition is invalid.
        """
        service = MoveOrderToEditingService()
        result = service.execute(order=self.order, user=self.user)

        AuditLogService.log_auto(
            actor=self.user,
            action="MOVE_TO_EDITING",
            target="orders.Order",
            target_id=self.order.id,
            metadata={
                "status": "under_editing"
            }
        )

        return result