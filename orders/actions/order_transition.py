
from orders.actions.base import BaseOrderAction
from orders.services.order_transition import OrderTransitionService
from audit_logging.services import log_audit_action
from orders.registry.decorator import register_order_action
@register_order_action("order_transition")
class OrderTransitionAction(BaseOrderAction):
    """
    Action to transition an order to a new status.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        old_status = self.order.status
        service = OrderTransitionService()
        result = service.transition(self.order_id, **self.params)

        new_status = self.order.status  # assumes service updates `self.order`
        log_audit_action(
            actor=self.user,
            action="TRANSITION",
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, new_status]},
            metadata={"params": self.params}
        )
        return result