
from orders.actions.base import BaseOrderAction
from orders.services.submit_order_service import SubmitOrderService
from orders.services.revisions import OrderRevisionService
from orders.order_enums import OrderStatus

from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("submit_revision")
class SubmitRevisionAction(BaseOrderAction):
    """
    Action to submit a revision request for an order.
    This is typically used when a user requests changes to an order.
    """
    def execute(self):
        service = OrderRevisionService(order=self.order, user=self.user)
        result = service.request_revision(reason=self.params["reason"])

        if result:
            AuditLogService.log_auto(
                actor=self.user,
                action="SUBMIT_REVISION_REQUEST",
                target="orders.Order",
                target_id=self.order.id,
                metadata={"reason": self.params["reason"]},
            )
        return result

@register_order_action("deny_revision")
class DenyRevisionAction(BaseOrderAction):
    """
    Action to deny a revision request for an order.
    This is typically used when an admin rejects a user's revision request.
    """

    def execute(self):
        reason = self.params.get("reason")
        if not reason:
            raise ValueError("A reason is required to deny a revision request.")

        service = OrderRevisionService(order=self.order, user=self.user)
        result = service.deny_revision(reason)

        if result:
            AuditLogService.log_auto(
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

@register_order_action("process_revision")
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
            AuditLogService.log_auto(
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

@register_order_action("request_revision")
class OrderRevisionAction(BaseOrderAction):
    """
    Action to request a revision for an order.
    This is typically used when a user wants to request changes to an order.
    """
    def execute(self):
        service = OrderRevisionService()
        result = service.request_revision(self.order_id, **self.params)

        AuditLogService.log_auto(
            actor=self.user,
            action="REQUEST_REVISION",
            target="orders.Order",
            target_id=self.order_id,
            metadata={"params": self.params}
        )
        return result