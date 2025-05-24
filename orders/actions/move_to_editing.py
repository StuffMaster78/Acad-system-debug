from orders.actions.base import BaseOrderAction
from orders.services.move_to_editing import MoveOrderToEditingService
from audit_logging.services import log_audit_action



class MoveOrderToEditingAction(BaseOrderAction):
    """
    Action to transition an order to 'under_editing' status.
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

        log_audit_action(
            actor=self.user,
            action="MOVE_TO_EDITING",
            target="orders.Order",
            target_id=self.order.id,
            metadata={
                "status": "under_editing"
            }
        )

        return result