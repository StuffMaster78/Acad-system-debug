from orders.actions.base import BaseOrderAction
from orders.services.mark_order_as_paid_service import MarkOrderPaidService
from audit_logging.services import log_audit_action


class MarkOrderPaidAction(BaseOrderAction):
    def execute(self):
        service = MarkOrderPaidService()
        result = service.mark_paid(self.order_id)

        log_audit_action(
            actor=self.user,
            action="MARK_PAID",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order marked as paid."}
        )
        return result