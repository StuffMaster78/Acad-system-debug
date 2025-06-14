# orders/actions/creation.py

from orders.actions.base import BaseOrderAction
from orders.services.create_order_service import CreateOrderService
from audit_logging.services import log_audit_action

class CreateOrderAction(BaseOrderAction):
    # action_name = "create_order"
    def execute(self):
        service = CreateOrderService()
        order = service.create_order(**self.params)

        log_audit_action(
            actor=self.user,
            action="CREATE_ORDER",
            target="orders.Order",
            target_id=order.id,
            metadata={"params": self.params}
        )
        return order