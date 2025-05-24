from orders.actions.base import BaseOrderAction
from orders.services.order_hold_service import HoldOrderService
from audit_logging.services import log_audit_action



class HoldOrderAction(BaseOrderAction):
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