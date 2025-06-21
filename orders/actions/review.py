from orders.actions.base import BaseOrderAction
from orders.services.review_order_service import ReviewOrderService
from audit_logging.services import log_audit_action
from orders.registry.decorator import register_order_action
@register_order_action("review_order")
class ReviewOrderAction(BaseOrderAction):
    def execute(self):
        service = ReviewOrderService()
        result = service.review_order(self.order_id)

        log_audit_action(
            actor=self.user,
            action="REVIEW",  # Add to ACTION_CHOICES if needed
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order reviewed."}
        )

        return result