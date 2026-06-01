from orders.actions.base import BaseOrderAction
from orders.services.status_transition_service import StatusTransitionService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action

@register_order_action("status_transition")
class StatusTransitionAction(BaseOrderAction):
    """
    Transitions an order to a new status.
    This action is typically used for manual operations, like an admin action.
    It allows for changing the status of an order based on the provided parameters.
    The parameters should include the new status and any other necessary details.
    The action logs the transition in the audit log for tracking purposes.
    The action expects the `order_id` and `params` to be set in the BaseOrderAction class.
    The `params` should include the new status and any additional information required for
    """
    def execute(self):
        old_status = self.order.status
        target_status = self.params.pop("target_status", None) or self.params.pop("new_status", None)
        if not target_status:
            raise ValueError("target_status is required for status_transition.")

        service = StatusTransitionService(user=self.user)
        result = service.transition_order_to_status(
            self.order,
            target_status=target_status,
            metadata=self.params,
        )
        new_status = self.order.status

        AuditLogService.log_auto(
            actor=self.user,
            action="STATUS_TRANSITION",
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"params": self.params}
        )
        return result
