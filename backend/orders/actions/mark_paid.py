from orders.actions.base import BaseOrderAction
from orders.services.mark_order_as_paid_service import MarkOrderPaidService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action

# Register with both names for compatibility
@register_order_action("mark_order_paid")
@register_order_action("mark_paid")
class MarkOrderPaidAction(BaseOrderAction):
    """
    Action to mark a specific order as paid.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        # Get optional reference_id and payment_method from params
        reference_id = getattr(self, 'reference_id', None) or (self.params.get('reference_id') if hasattr(self, 'params') else None)
        payment_method = getattr(self, 'payment_method', None) or (self.params.get('payment_method') if hasattr(self, 'params') else None)
        
        service = MarkOrderPaidService()
        result = service.mark_paid(
            self.order_id,
            reference_id=reference_id,
            payment_method=payment_method
        )

        AuditLogService.log_auto(
            actor=self.user,
            action="MARK_PAID",
            target="orders.Order",
            target_id=self.order_id,
            metadata={
                "message": "Order marked as paid.",
                "reference_id": reference_id,
                "payment_method": payment_method
            }
        )
        return result