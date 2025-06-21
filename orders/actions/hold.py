from orders.actions.base import BaseOrderAction
from orders.services.order_hold_service import HoldOrderService
from audit_logging.services import log_audit_action
from orders.registry.decorator import register_order_action
@register_order_action("hold_order")
class HoldOrderAction(BaseOrderAction):
    """
    Action to hold or resume a specific order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = HoldOrderService()
        action = "RESUME_ORDER" if self.params.get("resume") else "HOLD_ORDER"

        result = (
            service.resume_order(self.order_id)
            if self.params.get("resume")
            else service.hold_order(self.order_id)
        )

        log_audit_action(
            actor=self.user,
            action=action,
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "resume": self.params.get("resume", False)
            }
        )
        return result