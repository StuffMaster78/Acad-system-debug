from orders.actions.base import BaseOrderAction
from orders.services.rate_order_service import RateOrderService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("rate_order")
class RateOrderAction(BaseOrderAction):
    """
    Action to rate a specific order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = RateOrderService()
        result = service.rate_order(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="RATE",  # Add this to ACTION_CHOICES
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "message": "Order rated.",
                "rating": self.params.get("rating"),
                "comment": self.params.get("comment")
            }
        )

        return result