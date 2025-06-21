from orders.actions.base import BaseOrderAction
from orders.services.reopen_order_service import ReopenOrderService
from audit_logging.services import log_audit_action
from orders.registry.decorator import register_order_action
@register_order_action("reopen_order")
class ReopenOrderAction(BaseOrderAction):
    """
    Action to reopen an order that was previously closed.
    This action changes the order status from 'closed' to 'open'.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        old_status = self.order.status
        service = ReopenOrderService()
        result = service.reopen_order(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="REOPEN",
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, "open"]},
            metadata={"message": "Order reopened."}
        )
        return result