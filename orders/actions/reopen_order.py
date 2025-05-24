from orders.actions.base import BaseOrderAction
from orders.services.reopen_order_service import ReopenOrderService
from audit_logging.services import log_audit_action


class ReopenOrderAction(BaseOrderAction):
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