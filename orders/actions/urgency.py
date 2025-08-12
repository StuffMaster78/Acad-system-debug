from orders.actions.base import BaseOrderAction
from orders.services.order_urgency import OrderUrgencyService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("set_order_urgency")
class OrderUrgencyAction(BaseOrderAction):
    def execute(self):
        service = OrderUrgencyService()
        result = service.set_urgency(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="SET_URGENCY",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order urgency updated.", "params": self.params}
        )
        return result