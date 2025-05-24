
from orders.actions.base import BaseOrderAction
from orders.services.pricing_calculator import PricingCalculatorService
from audit_logging.services import log_audit_action


class PricingCalculatorAction(BaseOrderAction):
    def execute(self):
        service = PricingCalculatorService()
        result = service.calculate(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="CALCULATE_PRICING",
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "params": self.params,
                "result_summary": str(result)[:100]
            }
        )

        return result