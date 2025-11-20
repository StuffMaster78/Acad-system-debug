
from orders.actions.base import BaseOrderAction
from orders.services.reassignment import ReassignmentRequest
from orders.services.reassignment import OrderReassignmentService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("reassignment_request")
class ReassignmentRequestAction(BaseOrderAction):
    """
    Action to create a reassignment request for an order.
    This is typically used when a writer requests a reassignment.
    """
    def execute(self):
        reassignment = ReassignmentRequest.objects.create(**self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="CREATE_REASSIGNMENT_REQUEST",
            target="orders.ReassignmentRequest",
            target_id=reassignment.id,
            metadata={"params": self.params}
        )
        return reassignment
    
@register_order_action("reassign_order")
class OrderReassignmentAction(BaseOrderAction):
    """
    Action to reassign an order to a new writer.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = OrderReassignmentService()
        result = service.reassign(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="REASSIGN_ORDER",
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "message": "Order reassigned.",
                "reassigned_to": self.params.get("new_writer_id"),
                "reason": self.params.get("reason"),
                "params": self.params,
            }
        )
        return result