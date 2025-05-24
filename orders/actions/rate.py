from orders.actions.base import BaseOrderAction
from orders.services.rate_order_service import RateOrderService
from audit_logging.services import log_audit_action

class RateOrderAction(BaseOrderAction):
    def execute(self):
        service = RateOrderService()
        result = service.rate_order(self.order_id, **self.params)

        log_audit_action(
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