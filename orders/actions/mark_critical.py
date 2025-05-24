
from orders.actions.base import BaseOrderAction
from orders.services.mark_critical_order_service import MarkCriticalOrderService
from audit_logging.services import log_audit_action

class MarkCriticalAction(BaseOrderAction):
    def execute(self):
        service = MarkCriticalOrderService()
        result = service.mark_critical(self.order_id)

        log_audit_action(
            actor=self.user,
            action="MARK_CRITICAL",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order marked as critical."}
        )
        return result
