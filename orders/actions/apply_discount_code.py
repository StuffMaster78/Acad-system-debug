from orders.actions.base import BaseOrderAction
from orders.services.apply_discount_code_service import ApplyDiscountCodeService
from audit_logging.services import log_audit_action

# Lazy import avoids circular reference issue
from orders.registry.decorator import register_order_action

@register_order_action("apply_discount_code")
class ApplyDiscountCodeAction(BaseOrderAction):
    """
    Action to apply one or more discount codes to an order.

    Expected self.params:
        - codes (list[str]): List of discount codes to apply.
        - user (User): The user applying the codes (optional, usually admin).

    Returns:
        dict: Result from ApplyDiscountCodeService.
    """

    def execute(self):
        codes = self.params.get("codes", [])
        user = self.params.get("user", self.user)

        service = ApplyDiscountCodeService()
        result = service.apply_discounts_to_order(
            self.order_id,
            codes,
            user
        )

        log_audit_action(
            actor=self.user,
            action="DISCOUNT_CODE",
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "message": "Discount code(s) applied.",
                "codes": codes,
                "applied_by": user.id if user else None
            }
        )

        return result