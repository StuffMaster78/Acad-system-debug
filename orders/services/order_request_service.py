from urllib import request
from django.core.exceptions import ValidationError

from orders.models import OrderRequest, Order
from audit_logging.services import log_audit_action
from orders.exceptions import (
    OrderTransitionError,
    AlreadyAssignedError,
    RequestNotFoundError,
)
from orders.utils.order_utils import save_order
from orders.order_enums import OrderRequestStatus
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class OrderRequestService:
    """
    Service to manage writer interest and admin assignments.
    This service allows writers to request orders and enables admins to accept or reject these requests.
    It also provides methods to cancel requests and retrieve requests for orders or writers.
    The service is initialized with an optional user, which can be used for logging actions.
    """

    def __init__(self, user=None):
        """
        Initialize the service with an optional user.
        Args:
            user (User, optional): The user performing the action. Defaults to None.
        """
        self.user = user

    def create_request(self, order, writer, message=""):
        """
        Create a new writer request for an order.

        Args:
            order (Order): The target order.
            writer (User): Writer making the request.
            message (str): Optional message from the writer.

        Returns:
            OrderRequest: The created request.

        Raises:
            ValidationError: If the writer has already requested the order.
        """
        if OrderRequest.objects.filter(order=order, writer=writer).exists():
            raise ValidationError("You already requested this order.")

        request = OrderRequest.objects.create(
            order=order,
            writer=writer,
            message=message,
            website=order.website,
            status=OrderRequestStatus.PENDING,
            expires_at=timezone.now() + timezone.timedelta(minutes=15),
        )

        if self.user:
            log_audit_action(
                actor=self.user,
                action="CREATE_REQUEST",
                target="orders.OrderRequest",
                target_id=request.id,
                metadata={"order_id": order.id}
            )

        # Optionally notify admins here
        # notify_admin_new_request.delay(request.id)

        return request
    
    def get_requests_for_order(self, order, status=None):
        """
        Retrieve all requests for a specific order.

        Args:
            order (Order): The order to retrieve requests for.
            status (OrderRequestStatus, optional): Filter by status.

        Returns:
            QuerySet: OrderRequest objects for the specified order.

        Raises:
            ValidationError: If status is not valid.
        """
        if status and status not in OrderRequestStatus.values:
            raise ValidationError("Invalid status filter provided.")

        qs = OrderRequest.objects.filter(order=order)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')


    def get_writer_requests(self, writer, status=None):
        """
        Retrieve all requests made by a specific writer.

        Args:
            writer (User): The writer to retrieve requests for.
            status (OrderRequestStatus, optional): Filter by request status.

        Returns:
            QuerySet: OrderRequest objects for the specified writer.

        Raises:
            ValidationError: If input is invalid.
        """
        if not isinstance(writer, User):
            raise ValidationError("Writer must be a valid User instance.")

        if status and status not in OrderRequestStatus.values:
            raise ValidationError("Invalid status value provided.")

        qs = OrderRequest.objects.filter(writer=writer)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')


    def accept_writer(self, order, writer):
        """
        Accept a writer's request and assign the writer to the order.

        Args:
            order (Order): The order to assign.
            writer (User): The writer to assign.

        Returns:
            Order: The updated order.

        Raises:
            ValidationError: If the writer didn't request this order.
        """
        if order.status != "available":
            raise OrderTransitionError(
                f"Cannot assign writer. Order status is '{order.status}', "
                f"but must be 'available'."
            )
        if order.assigned_to is not None:
            raise AlreadyAssignedError("Order is already assigned to a writer.")

        writer_request = OrderRequest.objects.filter(
            order=order, writer=writer,
            status=OrderRequestStatus.PENDING,
        ).first()
        if not writer_request:
            raise RequestNotFoundError("No pending request from this writer.")

        # Accept selected
        writer_request.status = OrderRequestStatus.ACCEPTED
        writer_request.accepted_by_admin_at = timezone.now()
        writer_request.save(update_fields=["status", "accepted_by_admin_at"])

        # Reject others
        OrderRequest.objects.filter(
            order=order,
            status=OrderRequestStatus.PENDING
        ).exclude(writer=writer).update(status=OrderRequestStatus.REJECTED)

        # Assign writer
        order.assigned_to = writer
        order.status = "in_progress"
        save_order(order)

        if self.user:
            log_audit_action(
                actor=self.user,
                action="WRITER_ASSIGNED",
                target="orders.Order",
                target_id=order.id,
                changes={"status": ["available", "in_progress"]},
                metadata={"assigned_to": writer.id},
            )

        # notify_writer_on_acceptance.delay(writer_request.id)

        return writer_request

    def reject_request(self, order, writer, feedback=""):
        """
        Reject a writer's request for an order.

        Args:
            order (Order): The order to reject the request for.
            writer (User): The writer whose request is being rejected.
            feedback (str): Optional feedback for the writer.

        Returns:
            OrderRequest: The rejected request.
        """
        writer_request = OrderRequest.objects.filter(
            order=order, writer=writer,
            status=OrderRequestStatus.PENDING
        ).first()

        if not writer_request:
            raise RequestNotFoundError("No pending request from this writer.")

        writer_request.status = OrderRequestStatus.REJECTED
        writer_request.rejection_feedback = feedback or "Your request was rejected."
        writer_request.save(update_fields=["status", "rejection_feedback"])

        if self.user:
            log_audit_action(
                actor=self.user,
                action="REJECT_REQUEST",
                target="orders.OrderRequest",
                target_id=writer_request.id,
                metadata={"order_id": order.id, "writer_id": writer.id}
            )
        # Optionally notify the writer about rejection (TODO)
        # notify_writer_rejection.delay(writer_request.id, feedback)

        return writer_request

    def expire_pending_requests(self, order):
        """
        Expire all pending requests for a specific order.

        Args:
            order (Order): The order to expire requests for.

        Returns:
            int: The number of expired requests.
        """
        expired_requests = OrderRequest.objects.filter(
            order=order,
            status=OrderRequestStatus.PENDING,
            created_at__lt=now() - timedelta(days=1)
        )
        count = expired_requests.count()
        for request in expired_requests:
            request.status = OrderRequestStatus.EXPIRED
            request.save(update_fields=["status"])

        if self.user:
            log_audit_action(
                actor=self.user,
                action="EXPIRE_REQUEST",
                target="orders.OrderRequest",
                target_id=request.id,
                metadata={"order_id": order.id}
            )

        return count

    def withdraw_request(self, order, writer):
        """
        Withdraw a writer's request for an order.

        Args:
            order (Order): The order to withdraw from.
            writer (User): The writer withdrawing the request.

        Returns:
            OrderRequest: The withdrawn request.

        Raises:
            ValidationError: If the request does not exist or is not pending.
        """
        request = OrderRequest.objects.filter(
            order=order, writer=writer,
           status=OrderRequestStatus.PENDING,
        ).first()
        if not request:
            raise RequestNotFoundError("No pending request found for this order.")

        request.status = OrderRequestStatus.WITHDRAWN
        
        request.rejection_feedback = "Writer withdrew their request."
        request.save(update_fields=["withdrawn", "rejection_feedback"])

        if self.user:
            log_audit_action(
                actor=self.user,
                action="WITHDRAW_REQUEST",
                target="orders.OrderRequest",
                target_id=request.id,
                metadata={"order_id": order.id}
            )

        return request
    
    def reject_other_requests(self, order, accepted_writer):
        """
        Reject all other writer requests except the accepted one.

        Args:
            order (Order): The order in question.s
            accepted_writer (User): The accepted writer.
        """
        OrderRequest.objects.filter(
            order=order,
            status=OrderRequestStatus.PENDING,
        ).exclude(writer=accepted_writer).update(status=OrderRequestStatus.REJECTED)



    def expire_pending_requests(self, order):
        """
        Expire all pending order requests that have passed their expiration time.
        This method checks for requests that are still pending and have an expiration time
        that is less than the current time. It updates their status to EXPIRED and
        sets a rejection feedback message.
        Returns:
            int: The number of requests that were expired.
        """
        expired_requests = OrderRequest.objects.filter(
            order=order,
            status=OrderRequestStatus.PENDING,
            expires_at__lt=now()
        )

        count = expired_requests.count()

        for request in expired_requests:
            request.status = OrderRequestStatus.EXPIRED
            request.rejection_feedback = "Request expired due to no response."
            request.save(update_fields=["status", "rejection_feedback"])

        if self.user:
            log_audit_action(
                actor=self.user,
                action="EXPIRE_REQUEST",
                target="orders.OrderRequest",
                target_id=request.id,
                metadata={"order_id": order.id}
            )

        return count


    def reopen_request(self, request):
        """
        Reopen a previously rejected, withdrawn, or expired writer request.

        Args:
            request (OrderRequest): The request to reopen.

        Returns:
            OrderRequest: The updated request with status set to pending.

        Raises:
            ValidationError: If the request is not in a reopenable state.
        """
        from orders.order_enums import OrderRequestStatus

        if request.status not in [
            OrderRequestStatus.REJECTED,
            OrderRequestStatus.WITHDRAWN,
            OrderRequestStatus.EXPIRED
        ]:
            raise ValidationError(
                f"Cannot reopen request in status '{request.status}'. "
                "Only rejected, withdrawn, or expired requests can be reopened."
            )

        request.status = OrderRequestStatus.PENDING
        request.rejection_feedback = ""
        request.save(update_fields=["status", "rejection_feedback"])

        if self.user:
            log_audit_action(
                actor=self.user,
                action="REOPEN_REQUEST",
                target="orders.OrderRequest",
                target_id=request.id,
                metadata={"order_id": request.order.id}
            )

        return request

    def list_reopened_requests(self, order):
        """
        List all reopened writer requests for a given order.

        Args:
            order (Order): The order to filter requests for.

        Returns:
            QuerySet[OrderRequest]: All reopened requests for the order.
        """
        from orders.models import OrderRequest
        from orders.order_enums import OrderRequestStatus

        return OrderRequest.objects.filter(
            order=order,
            status=OrderRequestStatus.PENDING,
        ).exclude(
            rejection_feedback=""
        )

    def cancel_request(self, request):
        """
        Cancel a pending writer request.

        Args:
            request (OrderRequest): The request to cancel.

        Returns:
            OrderRequest: The updated request with status set to canceled.

        Raises:
            ValidationError: If the request is not in a cancellable state.
        """
        from orders.order_enums import OrderRequestStatus

        if request.status != OrderRequestStatus.PENDING:
            raise ValidationError(
                f"Cannot cancel request in status '{request.status}'. "
                "Only pending requests can be canceled."
            )

        request.status = OrderRequestStatus.CANCELED
        request.save(update_fields=["status"])

        if self.user:
            log_audit_action(
                actor=self.user,
                action="CANCEL_REQUEST",
                target="orders.OrderRequest",
                target_id=request.id,
                metadata={"order_id": request.order.id}
            )

        return request
    def list_requests_by_status(self, status):
        """
        List all requests by their status.

        Args:
            status (OrderRequestStatus): The status to filter requests by.

        Returns:
            QuerySet: A queryset of OrderRequest objects with the specified status.

        Raises:
            ValidationError: If the status is not valid.
        """
        from orders.order_enums import OrderRequestStatus

        if status not in OrderRequestStatus.values:
            raise ValidationError("Invalid request status provided.")

        return OrderRequest.objects.filter(status=status).order_by('-created_at')
    def list_requests_by_writer(self, writer):
        """
        List all requests made by a specific writer.
        Args:
            writer (User): The writer to filter requests by.
        Returns:
            QuerySet: A queryset of OrderRequest objects made by the specified writer.
        Raises:
            ValidationError: If the writer is not a valid User instance.
        """ 
        from orders.order_enums import OrderRequestStatus

        if not isinstance(writer, User):
            raise ValidationError("Writer must be a valid User instance.")

        return OrderRequest.objects.filter(writer=writer).order_by('-created_at')
    def list_requests_by_order(self, order):
        """
        List all requests for a specific order.
        Args:
            order (Order): The order to filter requests by.
        Returns:
            QuerySet: A queryset of OrderRequest objects for the specified order.
        Raises:
            ValidationError: If the order is not a valid Order instance.
        """
        from orders.order_enums import OrderRequestStatus

        if not isinstance(order, Order):
            raise ValidationError("Order must be a valid Order instance.")

        return OrderRequest.objects.filter(order=order).order_by('-created_at')