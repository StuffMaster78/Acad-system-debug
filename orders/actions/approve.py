from orders.actions.base import BaseOrderAction
from orders.services.approve_order_service import ApproveOrderService
from audit_logging.services import log_audit_action


class ApproveOrderAction(BaseOrderAction):
    # action_name = "approve_order"
    def execute(self):
        old_status = self.order.status

        service = ApproveOrderService()
        result = service.approve_order(self.order_id)

        new_status = "approved"

        log_audit_action(
            actor=self.user,
            action="APPROVE",  # Add this to your ACTION_CHOICES
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"message": "Order approved."}
        )

        return result
