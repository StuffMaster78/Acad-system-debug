from orders.models import WriterRequest, Order
from audit_logging.services.audit_log_service import AuditLogService
from orders.services.writer_request_service import WriterRequestService
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from orders.registry.decorator import register_order_action
@register_order_action("create_writer_request")
class CreateWriterRequestAction:
    """Handle creation of a writer request.

    Args:
        user (User): The writer user creating the request.
        order_id (int): ID of the order for which the request is made.
        data (dict): Request data including type, reason, and specifics.

    Returns:
        WriterRequest: The created WriterRequest instance.
    """
    def __init__(self, user, order_id, data):
        self.user = user
        self.order_id = order_id
        self.data = data

    def execute(self):
        """Create a writer request and log the audit action."""
        order = get_object_or_404(Order, id=self.order_id)

        request = WriterRequestService.create_request(
            order=order,
            writer=self.user,
            request_type=self.data['request_type'],
            reason=self.data['request_reason'],
            data=self.data
        )

        AuditLogService.log_auto(
            actor=self.user,
            action="CREATE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={
                "request_type": request.request_type,
                "reason": request.request_reason
            }
        )

        return request


class ClientRespondToWriterRequestAction:
    """Process client response to a writer request.

    Args:
        user (User): The client user responding to the request.
        request_id (int): ID of the WriterRequest to respond to.
        approve (bool): True to approve, False to decline.
        decline_reason (str, optional): Reason for declining.

    Returns:
        WriterRequest: The updated WriterRequest instance.
    """
    def __init__(self, user, request_id, approve, decline_reason=None):
        self.user = user
        self.request_id = request_id
        self.approve = approve
        self.decline_reason = decline_reason

    def execute(self):
        """Apply client response via service and log the audit."""
        writer_request = get_object_or_404(WriterRequest, id=self.request_id)

        WriterRequestService.client_respond(
            request=writer_request,
            client=self.user,
            approve=self.approve,
            reason=self.decline_reason
        )

        AuditLogService.log_auto(
            actor=self.user,
            action="CLIENT_RESPONDED_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=writer_request.id,
            metadata={
                "approved": self.approve,
                "reason": self.decline_reason
            }
        )

        return writer_request


class AdminOverrideWriterRequestAction:
    """Admin override for a writer request, optionally updating deadline.

    Args:
        user (User): The admin user performing override.
        request_id (int): ID of the WriterRequest to override.
        new_deadline (datetime.datetime, optional): New deadline to apply.

    Returns:
        WriterRequest: The updated WriterRequest instance.
    """
    def __init__(self, user, request_id, new_deadline=None):
        self.user = user
        self.request_id = request_id
        self.new_deadline = new_deadline

    def execute(self):
        """Perform admin override via service and log the audit."""
        writer_request = get_object_or_404(WriterRequest, id=self.request_id)

        WriterRequestService.admin_override(
            request=writer_request,
            admin=self.user,
            new_deadline=self.new_deadline
        )

        AuditLogService.log_auto(
            actor=self.user,
            action="ADMIN_OVERRIDE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=writer_request.id,
            metadata={
                "new_deadline": str(self.new_deadline) 
                                if self.new_deadline else None,
                "admin_approval": True,
            }
        )

        return writer_request