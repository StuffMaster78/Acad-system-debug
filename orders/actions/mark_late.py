
from orders.actions.base import BaseOrderAction
from audit_logging.services import log_audit_action
from orders.services.mark_late_order_service import MarkLateOrderService

class MarkLateOrderAction(BaseOrderAction):
    def execute(self):
        service = MarkLateOrderService()
        result = service.mark_late(self.order_id)

        log_audit_action(
            actor=self.user,
            action="MARK_LATE",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order marked as late."}
        )
        return result
