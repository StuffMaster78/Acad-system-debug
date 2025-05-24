
from orders.actions.base import BaseOrderAction
from orders.services.preferred_writer_service import PreferredWriterService
from orders.services.preferred_writer_response import PreferredWriterResponse
from audit_logging.services import log_audit_action


class PreferredWriterAction(BaseOrderAction):
    def execute(self):
        service = PreferredWriterService()
        result = service.set_preferred_writer(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="SET_PREFERRED_WRITER",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result


class PreferredWriterResponseAction(BaseOrderAction):
    def execute(self):
        service = PreferredWriterResponse()
        result = service.respond(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="PREFERRED_WRITER_RESPONSE",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result