
from orders.actions.base import BaseOrderAction
from orders.services.apply_discount_code_service import ApplyDiscountCodeService
from audit_logging.services import log_audit_action


class ApplyDiscountCodeAction(BaseOrderAction):
    # action_name = "apply_discount_to_order"
    def execute(self):
        codes = self.params.get("codes", [])
        user = self.params.get("user")

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