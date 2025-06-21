from orders.actions.base import BaseOrderAction
from orders.registry.decorator import register_order_action
from orders.services.approve_order_service import ApproveOrderService
from audit_logging.services import log_audit_action


@register_order_action("approve_order")
class ApproveOrderAction(BaseOrderAction):
    """
    Action to approve a specific order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        old_status = self.order.status

        service = ApproveOrderService()
        result = service.approve_order(self.order_id)

        new_status = "approved"

        log_audit_action(
            actor=self.user,
            action="APPROVE",  
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"message": "Order approved."}
        )

        return result