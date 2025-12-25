
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

        # Sanitize params for audit log (remove any non-serializable objects like User instances)
        import json
        sanitized_params = {}
        for key, value in self.params.items():
            try:
                # Try to serialize the value to check if it's JSON-serializable
                json.dumps(value)
                sanitized_params[key] = value
            except (TypeError, ValueError):
                # If not serializable, convert to a serializable format
                if hasattr(value, 'id'):
                    # Model instance - store ID and type
                    sanitized_params[key] = {
                        'id': value.id,
                        'type': value.__class__.__name__
                    }
                elif hasattr(value, '__dict__'):
                    # Object with __dict__ - convert to dict of serializable values
                    sanitized_params[key] = {
                        k: v for k, v in value.__dict__.items()
                        if isinstance(v, (str, int, float, bool, type(None)))
                    }
                else:
                    # Fallback: convert to string
                    sanitized_params[key] = str(value)
        
        AuditLogService.log_auto(
            actor=self.user,
            action="ASSIGN",
            target=self.order,
            metadata={"message": "Order assigned.", "params": sanitized_params}
        )
        return result