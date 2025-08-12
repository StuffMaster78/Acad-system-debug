
from orders.actions.base import BaseOrderAction
from orders.services.unpaid_order_service import UnpaidOrderService
from audit_logging.services.audit_log_service import AuditLogService  
from orders.registry.decorator import register_order_action
@register_order_action("handle_unpaid")
class UnpaidOrderAction(BaseOrderAction):
    def execute(self):
        service = UnpaidOrderService()
        result = service.handle_unpaid(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="HANDLE_UNPAID",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result