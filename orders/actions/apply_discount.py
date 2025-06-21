from orders.actions.base import BaseOrderAction
from orders.services.apply_direct_discount_service import ApplyDirectDiscountService
from audit_logging.services import log_audit_action
from orders.registry.decorator import register_order_action
@register_order_action("apply_direct_discount")
class ApplyDirectDiscountAction(BaseOrderAction):
    """"Action to apply a direct discount to an order.
    This action is typically used for manual operations, like an admin action.
    """
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