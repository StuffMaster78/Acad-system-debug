
from orders.actions.base import BaseOrderAction
from orders.services.reassignment import ReassignmentRequest
from orders.services.reassignment import OrderReassignmentService
from audit_logging.services import log_audit_action

class ReassignmentRequestAction(BaseOrderAction):
    def execute(self):
        reassignment = ReassignmentRequest.objects.create(**self.params)

        log_audit_action(
            actor=self.user,
            action="CREATE_REASSIGNMENT_REQUEST",
            target="orders.ReassignmentRequest",
            target_id=reassignment.id,
            metadata={"params": self.params}
        )
        return reassignment
    

class OrderReassignmentAction(BaseOrderAction):
    def execute(self):
        service = OrderReassignmentService()
        result = service.reassign(self.order_id, **self.params)

        log_audit_action(
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