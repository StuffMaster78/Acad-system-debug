from orders.actions.base import BaseOrderAction
from orders.registry.decorator import register_order_action
from orders.services.status_transition_service import StatusTransitionService
from audit_logging.services.audit_log_service import AuditLogService


@register_order_action("transition_to_pending")
class TransitionToPendingAction(BaseOrderAction):
    def execute(self):
        old_status = self.order.status
        new_status = "pending"

        service = StatusTransitionService()
        result = service.transition_order_to_status(
            self.order_id,
            target_status=new_status,
            performed_by=self.user
        )

        AuditLogService.log_auto(
            actor=self.user,
            action="STATUS_TRANSITION",
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"message": "Order transitioned to pending."}
        )

        return result