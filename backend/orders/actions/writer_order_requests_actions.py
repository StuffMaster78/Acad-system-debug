from django.core.exceptions import PermissionDenied
from orders.actions.base import BaseOrderAction
from orders.services.order_request_service import OrderRequestService
from django.contrib.auth import get_user_model
User = get_user_model()

class CreateWriterRequestAction(BaseOrderAction):
    """
    Action for a writer to request an available order.

    Writers use this action to express interest in working on an order.

    Expected `self.data`:
        - message (str, optional): Optional message attached to request.

    Returns:
        OrderRequest: The created writer request.
    """
    def execute(self):
        """Create a request for the order by the writer."""
        message = self.data.get("message", "")
        order = self.order or self.data.get("order")
        service = OrderRequestService(user=self.user)
        return service.create_request(self.order, self.user, message)


class AdminOverrideWriterRequestAction(BaseOrderAction):
    """
    Action for admins to assign a writer to an order via request.

    This assigns the specified writer and auto-rejects all other requests.
    Only staff/admins are allowed to invoke this action.

    Expected `self.data`:
        - writer (User): The writer to assign the order to.

    Returns:
        Order: The updated order instance.

    Raises:
        PermissionDenied: If the actor is not a staff/admin.
        ValidationError: If the writer did not request this order.
    """
    def execute(self):
        """Accept a writer request and assign the order to them."""
        if not self.order:
            raise ValueError("Order must be provided to accept a writer request.")
        if "writer" not in self.data:
            raise ValueError("Writer must be specified in the action data.")
        # Ensure the user is an admin
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can override writer requests.")

        writer = self.data["writer"]
        if isinstance(writer, int):
            writer = User.objects.get(id=writer)

        service = OrderRequestService(user=self.user)
        return service.accept_writer(self.order, writer)
    

class WithdrawWriterRequestAction(BaseOrderAction):
    """
    Writer withdraws their pending request.
    Expected data: none
    """
    def execute(self):
        """Withdraw the writer's request for the order."""
        if not self.order:
            raise ValueError("Order must be provided to withdraw a writer request.")
        if not self.user.is_authenticated:
            raise PermissionDenied("Only authenticated users can withdraw requests.")
        if not self.order.has_writer_request(self.user):
            raise ValueError("User has no request to withdraw for this order.")
        # Ensure the user is the one who made the request
        if not self.order.is_writer_request(self.user):
            raise PermissionDenied("Only the writer who made the request can withdraw it.")
        # Proceed with withdrawal
        if not self.order.is_pending_request(self.user):
            raise ValueError("Only pending requests can be withdrawn.")
        # Create the service and withdraw the request
        service = OrderRequestService(user=self.user)
        return service.withdraw_request(self.order, self.user)


class RejectWriterRequestAction(BaseOrderAction):
    """
    Admin explicitly rejects a specific writer request.
    Expected data:
        - request (OrderRequest or int): the request to reject
        - feedback (optional str)
    """
    def execute(self):
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can reject writer requests.")

        request = self.data.get("request")
        if isinstance(request, int):
            from orders.models import OrderRequest
            request = OrderRequest.objects.get(id=request)

        feedback = self.data.get("feedback", "")
        service = OrderRequestService(user=self.user)
        return service.reject_request(request, feedback)
class AcceptWriterRequestAction(BaseOrderAction):
    """
    Admin accepts a specific writer request.
    Expected data:
        - request (OrderRequest or int): the request to accept
    """
    def execute(self):
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can accept writer requests.")

        request = self.data.get("request")
        if isinstance(request, int):
            from orders.models import OrderRequest
            request = OrderRequest.objects.get(id=request)

        service = OrderRequestService(user=self.user)
        return service.accept_request(request)
class CancelWriterRequestAction(BaseOrderAction):
    """
    Admin cancels a specific writer request.
    Expected data:
        - request (OrderRequest or int): the request to cancel
    """
    def execute(self):
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can cancel writer requests.")

        request = self.data.get("request")
        if isinstance(request, int):
            from orders.models import OrderRequest
            request = OrderRequest.objects.get(id=request)

        service = OrderRequestService(user=self.user)
        return service.cancel_request(request)
class ListWriterRequestsAction(BaseOrderAction):
    """
    List all writer requests for the current order.

    Returns:
        list: A list of OrderRequest instances for the order.
    """
    def execute(self):
        """List all writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_requests(self.order)
class ListMyWriterRequestsAction(BaseOrderAction):
    """
    List all writer requests made by the current user.

    Returns:
        list: A list of OrderRequest instances made by the user.
    """
    def execute(self):
        """List all writer requests made by the user."""
        if not self.user.is_authenticated:
            raise PermissionDenied("Only authenticated users can list their requests.")
        service = OrderRequestService(user=self.user)
        return service.list_my_requests(self.user)
class ListPendingWriterRequestsAction(BaseOrderAction):
    """
    List all pending writer requests for the current order.

    Returns:
        list: A list of OrderRequest instances that are pending.
    """
    def execute(self):
        """List all pending writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list pending writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_pending_requests(self.order)
class ListAcceptedWriterRequestsAction(BaseOrderAction):
    """
    List all accepted writer requests for the current order.

    Returns:
        list: A list of OrderRequest instances that are accepted.
    """
    def execute(self):
        """List all accepted writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list accepted writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_accepted_requests(self.order)
class ListRejectedWriterRequestsAction(BaseOrderAction):
    """
    List all rejected writer requests for the current order.

    Returns:
        list: A list of OrderRequest instances that are rejected.
    """
    def execute(self):
        """List all rejected writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list rejected writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_rejected_requests(self.order)
class ListWithdrawnWriterRequestsAction(BaseOrderAction):
    """
    List all withdrawn writer requests for the current order.

    Returns:
        list: A list of OrderRequest instances that are withdrawn.
    """
    def execute(self):
        """List all withdrawn writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list withdrawn writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_withdrawn_requests(self.order) 

class ExpireWriterRequestAction(BaseOrderAction):
    """
    Admin manually expires a writer request.
    Expected data:
        - request (OrderRequest or int)
    """
    def execute(self):
        if not self.user.is_staff:
            raise PermissionDenied("Only admins can expire writer requests.")

        request = self.data.get("request")
        if isinstance(request, int):
            from orders.models import OrderRequest
            request = OrderRequest.objects.get(id=request)

        if not request.is_expired():
            raise ValueError("Request is not expired yet.")

        request.mark_expired()
        return request
class ListExpiredWriterRequestsAction(BaseOrderAction):
    """
    List all expired writer requests for the current order.

    Returns:
        list: A list of OrderRequest instances that are expired.
    """
    def execute(self):
        """List all expired writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list expired writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_expired_requests(self.order) 
    

class ReopenWriterRequestAction(BaseOrderAction):
    """
    Reopen a previously rejected, withdrawn, or expired writer request.

    Expected data:
        - request (OrderRequest or int): the request to reopen

    Returns:
        OrderRequest: The reopened writer request.
    """
    def execute(self):
        if not self.user.is_authenticated:
            raise PermissionDenied("Only authenticated users can reopen requests.")

        request = self.data.get("request")
        if isinstance(request, int):
            from orders.models import OrderRequest
            request = OrderRequest.objects.get(id=request)

        # Ensure the user owns the request
        if request.writer != self.user:
            raise PermissionDenied("You can only reopen your own requests.")

        service = OrderRequestService(user=self.user)
        return service.reopen_request(request)


class ListReopenedWriterRequestsAction(BaseOrderAction):
    """
    List all reopened writer requests for the current order.

    Returns:
        list: A list of OrderRequest instances that are reopened.
    """
    def execute(self):
        """List all reopened writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list reopened writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_reopened_requests(self.order)
class ListAllWriterRequestsAction(BaseOrderAction):
    """
    List all writer requests for the current order, regardless of status.

    Returns:
        list: A list of all OrderRequest instances for the order.
    """
    def execute(self):
        """List all writer requests for the order."""
        if not self.order:
            raise ValueError("Order must be provided to list all writer requests.")
        service = OrderRequestService(user=self.user)
        return service.list_all_requests(self.order)
class ListMyAllWriterRequestsAction(BaseOrderAction):
    """
    List all writer requests made by the current user, regardless of status.

    Returns:
        list: A list of all OrderRequest instances made by the user.
    """
    def execute(self):
        """List all writer requests made by the user."""
        if not self.user.is_authenticated:
            raise PermissionDenied("Only authenticated users can list their requests.")
        service = OrderRequestService(user=self.user)
        return service.list_my_all_requests(self.user)
class ListMyPendingWriterRequestsAction(BaseOrderAction):
    """
    List all pending writer requests made by the current user.

    Returns:
        list: A list of pending OrderRequest instances made by the user.
    """
    def execute(self):
        """List all pending writer requests made by the user."""
        if not self.user.is_authenticated:
            raise PermissionDenied("Only authenticated users can list their requests.")
        service = OrderRequestService(user=self.user)
        return service.list_my_pending_requests(self.user)
class ListMyAcceptedWriterRequestsAction(BaseOrderAction):
    """
    List all accepted writer requests made by the current user.

    Returns:
        list: A list of accepted OrderRequest instances made by the user.
    """
    def execute(self):
        """List all accepted writer requests made by the user."""
        if not self.user.is_authenticated:
            raise PermissionDenied("Only authenticated users can list their requests.")
        service = OrderRequestService(user=self.user)
        return service.list_my_accepted_requests(self.user)
    
class ListRequestsByStatusAction(BaseOrderAction):
    """
    List all writer requests for the current order by status.

    Expected data:
        - status (str): The status to filter requests by (e.g., 'pending', 'accepted', etc.).

    Returns:
        list: A list of OrderRequest instances filtered by the specified status.
    """
    def execute(self):
        """List all writer requests for the order by status."""
        if not self.order:
            raise ValueError("Order must be provided to list writer requests by status.")
        status = self.data.get("status")
        if not status:
            raise ValueError("Status must be specified in the action data.")
        service = OrderRequestService(user=self.user)
        return service.list_requests_by_status(self.order, status)
class ListMyRequestsByStatusAction(BaseOrderAction):
    """
    List all writer requests made by the current user by status.

    Expected data:
        - status (str): The status to filter requests by (e.g., 'pending', 'accepted', etc.).

    Returns:
        list: A list of OrderRequest instances made by the user filtered by the specified status.
    """
    def execute(self):
        """List all writer requests made by the user by status."""
        if not self.user.is_authenticated:
            raise PermissionDenied("Only authenticated users can list their requests.")
        status = self.data.get("status")
        if not status:
            raise ValueError("Status must be specified in the action data.")
        service = OrderRequestService(user=self.user)
        return service.list_my_requests_by_status(self.user, status)
class ListAllRequestsByStatusAction(BaseOrderAction):
    """
    List all writer requests for the current order by status, regardless of who made them.

    Expected data:
        - status (str): The status to filter requests by (e.g., 'pending', 'accepted', etc.).

    Returns:
        list: A list of all OrderRequest instances for the order filtered by the specified status.
    """
    def execute(self):
        """List all writer requests for the order by status."""
        if not self.order:
            raise ValueError("Order must be provided to list all writer requests by status.")
        status = self.data.get("status")
        if not status:
            raise ValueError("Status must be specified in the action data.")
        service = OrderRequestService(user=self.user)
        return service.list_all_requests_by_status(self.order, status)