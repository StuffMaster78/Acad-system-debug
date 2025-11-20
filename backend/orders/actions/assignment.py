
from orders.actions.base import BaseOrderAction
from orders.services.assignment import OrderAssignmentService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("assign_order")
class OrderAssignmentAction(BaseOrderAction):
    """
    Action to assign an order to a specific user or team.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = OrderAssignmentService()
        result = service.assign(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="ASSIGN",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order assigned.", "params": self.params}
        )
        return result