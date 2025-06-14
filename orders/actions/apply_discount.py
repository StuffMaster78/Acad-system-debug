from orders.actions.base import BaseOrderAction
from orders.services.apply_direct_discount_service import ApplyDirectDiscountService
from audit_logging.services import log_audit_action


class ApplyDirectDiscountAction(BaseOrderAction):
    # action_name = "apply_discount_action"
    def execute(self):
        service = ApplyDirectDiscountService()
        result = service.apply_discount(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="DISCOUNT",
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "message": "Direct discount applied.",
                "params": self.params
            }
        )
        return result