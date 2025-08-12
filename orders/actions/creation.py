# orders/actions/creation.py

from orders.actions.base import BaseOrderAction
from orders.services.create_order_service import CreateOrderService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("create_order")
class CreateOrderAction(BaseOrderAction):
    """
    Action to create a new order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = CreateOrderService()
        order = service.create_order(**self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="CREATE_ORDER",
            target="orders.Order",
            target_id=order.id,
            metadata={"params": self.params}
        )
        return order