from orders.actions.base import BaseOrderAction
from orders.services.order_urgency import OrderUrgencyService
from audit_logging.services import log_audit_action


class OrderUrgencyAction(BaseOrderAction):
    def execute(self):
        service = OrderUrgencyService()
        result = service.set_urgency(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="SET_URGENCY",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order urgency updated.", "params": self.params}
        )
        return result