
from orders.actions.base import BaseOrderAction
from orders.services.assignment import OrderAssignmentService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action

@register_order_action("assign_order")
class OrderAssignmentAction(BaseOrderAction):
    """
    Action to assign an order to a specific user or team.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        # Get writer_id from params
        writer_id = self.params.get('writer_id')
        if not writer_id:
            raise ValueError("writer_id is required for assign_order action")
        
        reason = self.params.get('reason', 'Assigned by admin')
        writer_payment_amount = self.params.get('writer_payment_amount')
        
        # Initialize service with order and set actor for admin override
        service = OrderAssignmentService(self.order)
        service.actor = self.user  # Set actor so admin/support can override constraints
        
        result = service.assign_writer(
            writer_id=writer_id,
            reason=reason,
            writer_payment_amount=writer_payment_amount
        )

        AuditLogService.log_auto(
            actor=self.user,
            action="ASSIGN",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"message": "Order assigned.", "params": self.params}
        )
        return result