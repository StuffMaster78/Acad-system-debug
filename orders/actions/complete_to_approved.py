
from orders.actions.base import BaseOrderAction
from audit_logging.services import log_audit_action
from orders.services.complete_to_approved_service import CompleteToApprovedService
from orders.registry.decorator import register_order_action
@register_order_action("complete_to_approved")
class CompleteToApprovedAction(BaseOrderAction):
    """
    Action to transition an order from completed to approved.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        old_status = self.order.status
        service = CompleteToApprovedService()
        result = service.complete_to_approved(self.order_id)
        new_status = self.order.status

        log_audit_action(
            actor=self.user,
            action="COMPLETE_TO_APPROVED",
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"message": "Order transitioned from completed to approved."}
        )
        return result