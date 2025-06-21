
from orders.actions.base import BaseOrderAction
from audit_logging.services import log_audit_action
from orders.services.mark_late_order_service import MarkLateOrderService
from orders.registry.decorator import register_order_action
@register_order_action("mark_late_order")
class MarkLateOrderAction(BaseOrderAction):
    """
    Action to mark a specific order as late.
    This is typically used for manual operations, like an admin action.
    """
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
