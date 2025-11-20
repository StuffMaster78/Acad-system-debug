
from orders.actions.base import BaseOrderAction
from orders.services.preferred_writer_service import PreferredWriterService
from orders.services.preferred_writer_response import PreferredWriterResponse
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("set_preferred_writer")
class PreferredWriterAction(BaseOrderAction):
    """
    Action to set a preferred writer for a specific order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = PreferredWriterService()
        result = service.set_preferred_writer(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="SET_PREFERRED_WRITER",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result

@register_order_action("preferred_writer_response")
class PreferredWriterResponseAction(BaseOrderAction):
    """
    Action to respond to a preferred writer request for a specific order.
    This is typically used for manual operations, like an admin action.
    """
    def execute(self):
        service = PreferredWriterResponse()
        result = service.respond(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="PREFERRED_WRITER_RESPONSE",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result