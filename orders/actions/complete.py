from orders.actions.base import BaseOrderAction
from orders.services.complete_order_service import CompleteOrderService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("complete_order")
class CompleteOrderAction(BaseOrderAction):
    """
    Action to mark an order as completed.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        old_status = self.order.status

        service = CompleteOrderService()
        result = service.complete_order(self.order_id)

        new_status = "completed"

        AuditLogService.log_auto(
            actor=self.user,
            action="COMPLETE",  # Add this to your ACTION_CHOICES
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"message": "Order marked as completed."}
        )

        return result