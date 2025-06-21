from orders.actions.base import BaseOrderAction
from orders.services.status_transition_service import StatusTransitionService
from audit_logging.services import log_audit_action
from orders.registry.decorator import register_order_action   

@register_order_action("status_transition")
class StatusTransitionAction(BaseOrderAction):
    def execute(self):
        old_status = self.order.status
        service = StatusTransitionService()
        result = service.transition(self.order_id, **self.params)
        new_status = self.order.status

        log_audit_action(
            actor=self.user,
            action="STATUS_TRANSITION",
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"params": self.params}
        )
        return result