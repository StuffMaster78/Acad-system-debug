from orders.actions.base import BaseOrderAction
from orders.services.complete_order_service import CompleteOrderService
from audit_logging.services import log_audit_action


class CompleteOrderAction(BaseOrderAction):
    # action_name = "complete_order"
    def execute(self):
        old_status = self.order.status

        service = CompleteOrderService()
        result = service.complete_order(self.order_id)

        new_status = "completed"

        log_audit_action(
            actor=self.user,
            action="COMPLETE",  # Add this to your ACTION_CHOICES
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"message": "Order marked as completed."}
        )

        return result