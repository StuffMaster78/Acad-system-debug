from orders.actions.base import BaseOrderAction
from orders.services.cancel_order_service import CancelOrderService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("cancel_order")
class CancelOrderAction(BaseOrderAction):
    """
    Action to cancel a specific order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        old_status = self.order.status

        service = CancelOrderService()
        result = service.cancel_order(self.order_id, self.reason, user=self.user)

        new_status = "cancelled"

        AuditLogService.log_auto(
            actor=self.user,
            action="DELETE",  
            target="orders.Order", 
            target_id=self.order_id,
            metadata={"reason": self.reason},
            changes={"status": [old_status, new_status]},
        )

        return result
        # notify_order_cancellation(self.order_id)