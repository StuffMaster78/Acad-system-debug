
from orders.actions.base import BaseOrderAction
from orders.services.submit_order_service import SubmitOrderService
from orders.services.revisions import OrderRevisionService
from orders.order_enums import OrderStatus

from audit_logging.services import log_audit_action


class SubmitRevisionAction(BaseOrderAction):
    def execute(self):
        service = OrderRevisionService(order=self.order, user=self.user)
        result = service.request_revision(reason=self.params["reason"])

        if result:
            log_audit_action(
                actor=self.user,
                action="SUBMIT_REVISION_REQUEST",
                target="orders.Order",
                target_id=self.order.id,
                metadata={"reason": self.params["reason"]},
            )
        return result

class DenyRevisionAction(BaseOrderAction):
    """
    Action to deny a revision request for an order.
    """

    def execute(self):
        reason = self.params.get("reason")
        if not reason:
            raise ValueError("A reason is required to deny a revision request.")

        service = OrderRevisionService(order=self.order, user=self.user)
        result = service.deny_revision(reason)

        if result:
            log_audit_action(
                actor=self.user,
                action="DENY_REVISION",
                target="orders.Order",
                target_id=self.order.id,
                metadata={
                    "denied_reason": reason,
                    "from_status": OrderStatus.COMPLETED.value,
                    "to_status": OrderStatus.REVISION_DENIED.value,
                },
            )
        return result
    
class ProcessRevisionAction(BaseOrderAction):
    """
    Action to submit the revised work and mark the order complete again.
    """

    def execute(self):
        revised_work = self.params.get("revised_work")
        if not revised_work:
            raise ValueError("Revised work content is required.")

        service = OrderRevisionService(order=self.order, user=self.user)
        result = service.process_revision(revised_work)

        if result:
            log_audit_action(
                actor=self.user,
                action="PROCESS_REVISION",
                target="orders.Order",
                target_id=self.order.id,
                metadata={
                    "from_status": OrderStatus.IN_REVISION.value,
                    "to_status": OrderStatus.COMPLETED.value,
                    "revised_by": str(self.user),
                },
            )
        return result

class OrderRevisionAction(BaseOrderAction):
    def execute(self):
        service = OrderRevisionService()
        result = service.request_revision(self.order_id, **self.params)

        log_audit_action(
            actor=self.user,
            action="REQUEST_REVISION",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result