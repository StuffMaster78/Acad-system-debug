
from orders.actions.base import BaseOrderAction
from orders.services.pricing_calculator import PricingCalculatorService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
from orders.services.order_pricing_snapshot import OrderPricingSnapshotService 

@register_order_action("calculate_pricing")
class PricingCalculatorAction(BaseOrderAction):
    """
    Action to calculate pricing for a specific order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = PricingCalculatorService(self.order)
        breakdown = service.calculate_breakdown()

        # If save=true is passed in params, persist snapshot
        if self.params.get("save") is True:
            OrderPricingSnapshotService.save_snapshot(
                order=self.order,
                pricing_data=breakdown
            )

        AuditLogService.log_auto(
            actor=self.user,
            action="CALCULATE_PRICING",
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "params": self.params,
                "final_total": breakdown.get("final_total"),
                "base_price": breakdown.get("base_price"),
                "summary": f"{breakdown.get('final_total')} after discount"
            }
        )

        return breakdown