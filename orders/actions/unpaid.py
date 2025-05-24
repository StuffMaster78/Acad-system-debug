
from orders.actions.base import BaseOrderAction
from orders.services.unpaid_order_service import UnpaidOrderService
from audit_logging.services import log_audit_action  


class UnpaidOrderAction(BaseOrderAction):
    def execute(self):
        service = UnpaidOrderService()
        result = service.handle_unpaid(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="HANDLE_UNPAID",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result