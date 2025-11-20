from __future__ import annotations

from datetime import datetime
from django.shortcuts import get_object_or_404

from orders.models import WriterRequest, Order
from audit_logging.services.audit_log_service import AuditLogService
from orders.services.writer_request_service import WriterRequestService

from orders.actions.base import BaseOrderAction
from orders.registry.decorator import register_order_action


@register_order_action("create_writer_request")
class CreateWriterRequestAction(BaseOrderAction):
    """
    Create a writer request and log the action.
    Expects params: user, data (with request_type, request_reason, ...)
    """

    def execute(self) -> WriterRequest:
        user = self.params["user"]
        data = self.params["data"]

        order = get_object_or_404(Order, id=self.order_id)

        req = WriterRequestService.create_request(
            order=order,
            writer=user,
            request_type=data["request_type"],
            reason=data["request_reason"],
            data=data,
        )

        AuditLogService.log_auto(
            actor=user,
            action="CREATE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=req.id,
            metadata={
                "request_type": req.request_type,
                "reason": req.request_reason,
            },
        )
        return req


@register_order_action("client_respond_writer_request")
class ClientRespondToWriterRequestAction(BaseOrderAction):
    """
    Client approves/declines a writer request and logs it.
    Expects params: user, request_id, approve, decline_reason (optional)
    """

    def execute(self) -> WriterRequest:
        user = self.params["user"]
        request_id = self.params["request_id"]
        approve = self.params["approve"]
        decline_reason = self.params.get("decline_reason")

        wr = get_object_or_404(WriterRequest, id=request_id)

        WriterRequestService.client_respond(
            request=wr,
            client=user,
            approve=approve,
            reason=decline_reason,
        )

        AuditLogService.log_auto(
            actor=user,
            action="CLIENT_RESPONDED_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=wr.id,
            metadata={"approved": approve, "reason": decline_reason},
        )
        return wr


@register_order_action("admin_override_writer_request")
class AdminOverrideWriterRequestAction(BaseOrderAction):
    """
    Admin override on a writer request, optionally updating deadline.
    Expects params: user, request_id, new_deadline (datetime | None)
    """

    def execute(self) -> WriterRequest:
        user = self.params["user"]
        request_id = self.params["request_id"]
        new_deadline: datetime | None = self.params.get("new_deadline")

        wr = get_object_or_404(WriterRequest, id=request_id)

        WriterRequestService.admin_override(
            request=wr,
            admin=user,
            new_deadline=new_deadline,
        )

        AuditLogService.log_auto(
            actor=user,
            action="ADMIN_OVERRIDE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=wr.id,
            metadata={
                "new_deadline": (
                    new_deadline.isoformat() if new_deadline else None
                ),
                "admin_approval": True,
            },
        )
        return wr


# Some registries look for this; harmless and makes discovery bulletproof.
ACTIONS = [
    CreateWriterRequestAction,
    ClientRespondToWriterRequestAction,
    AdminOverrideWriterRequestAction,
]

# Optional: make star-imports safe if your loader uses __all__.
__all__ = [a.__name__ for a in ACTIONS]
