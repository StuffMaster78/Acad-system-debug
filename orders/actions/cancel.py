from orders.actions.base import BaseOrderAction
from orders.services.cancel_order_service import CancelOrderService
from audit_logging.services import log_audit_action

class CancelOrderAction(BaseOrderAction):
    def execute(self):
        old_status = self.order.status

        service = CancelOrderService()
        result = service.cancel_order(self.order_id, self.reason)

        new_status = "cancelled"

        log_audit_action(
            actor=self.user,
            action="DELETE",  
            target="orders.Order", 
            target_id=self.order_id,
            metadata={"reason": self.reason},
            changes={"status": [old_status, new_status]},
        )

        return result
        # notify_order_cancellation(self.order_id)