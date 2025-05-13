import logging
from typing import Any, Dict
from .base import OrderActionHandler
from orders.models import Order
from orders.services.order_service import OrderService
from django.core.exceptions import ValidationError
from orders.services.revisions import (
    request_revision, process_revision,
    deny_revision
)
from orders.exceptions import TransitionNotAllowed
from notifications_system.utils import (
    send_website_mail, send_notification
)
from order_configs.models import RevisionPolicyConfig
from datetime import timedelta
from django.utils import timezone
from users.models import User
from orders.models import OrderStatus
from orders.services.reassignment import (
    create_reassignment_request,
    resolve_reassignment_request
)
from orders.services.utils import is_admin_or_support

logger = logging.getLogger(__name__)

class OrderActionHandler:
    """
    Base class for handling order actions.
    Each order action (e.g., transition, assign, complete) is a subclass of this.
    """
    def __init__(self, order: Order,user: User, data: dict = None, *args, **kwargs):
        self.order = order
        self.user = user
        self.data = data or {}

    def is_allowed(self) -> bool:
        """
        Determines whether the action can be performed on the given order.

        :param order: The order object.
        :return: bool indicating if the action is allowed.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def perform(self, *args, **kwargs):
        """
        Performs the action on the given order.

        :param order: The order object.
        :raises: TransitionNotAllowed if the action is not allowed.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Executes the action after checking if it is allowed.
        This combines both the `is_allowed` and `perform` methods.

        :param order: The order object.
        :param args: Additional arguments passed to `perform`.
        :param kwargs: Additional keyword arguments passed to `perform`.
        :return: The modified order after performing the action.
        :raises: TransitionNotAllowed if the action is not allowed.
        """
        if not self.is_allowed():
            raise TransitionNotAllowed("Action is not allowed for this order.")
        return self.perform(*args, **kwargs)

class CreateOrderAction(OrderActionHandler):
    """
    Action handler for creating a new order.
    This action is triggered when a client or admin
    requests to create a new order.
    """

    def __init__(self, user: User, order_data: Dict[str, Any], *args: Any,
                 **kwargs: Any):
        """
        Initializes the order creation handler.

        :param user: The user initiating the order creation (typically the
            client).
        :param order_data: The data for creating the order, like product
            details.
        """
        self.user = user
        self.order_data = order_data
        super().__init__(order=None, user=user, *args, **kwargs)

    def is_allowed(self) -> bool:
        """
        Determines whether the user is allowed to create an order.
        In this case, we can assume that any authenticated user can create
        an order. Add more complex checks based on your application logic.

        :return: True if the order can be created.
        """
        if not self.user.is_authenticated:
            raise TransitionNotAllowed(
                "User must be authenticated to create an order."
            )
        
        # Check if the user is a client, support, or admin
        if self.user.role not in ['client', 'superadmin', 'support', 'admin']:
            raise TransitionNotAllowed(
                "You are not allowed to create an order."
            )
        
        # Add more complex role checks here if needed.
        return True

    def perform(self) -> Order:
        """
        Perform the order creation by passing data to the service layer.

        :raises: ValidationError if the data is invalid.
        :return: The created order object.
        """
        if not self.is_allowed():
            raise TransitionNotAllowed("User is not allowed to create an "
                                       "order.")

        try:
            # Create the order using the service layer.
            new_order = OrderService.create_order(self.user, self.order_data)
            return new_order
        except ValidationError as e:
            # Log validation error and raise appropriate exception.
            logger.error(f"Error creating order for user {self.user.id}: {e}")
            raise e
        except Exception as e:
            # Catch any other unexpected exceptions.
            logger.error(f"Unexpected error while creating order: {e}")
            raise TransitionNotAllowed(f"Failed to create order: {str(e)}")

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Executes the order creation action. This method checks if the action
        is allowed and performs the creation.

        :return: The created order object.
        :raises: TransitionNotAllowed if the action is not allowed.
        """
        if not self.is_allowed():
            raise TransitionNotAllowed("Action is not allowed to create the "
                                       "order.")
        return self.perform()


class TransitionToPending(OrderActionHandler):
    """
    Transition the order to the 'pending' state.
    """
    def is_allowed(self) -> bool:
        return self.order.status in ['unpaid', 'available']

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order cannot be moved to 'pending' from the current status."
            )
        return OrderService.transition_to_pending(self.order)


class PutOnHold(OrderActionHandler):
    """
    Puts the order on hold.
    """
    def is_allowed(self) -> bool:
        return self.order.status == 'assigned'

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be put on hold."
            )
        return OrderService.put_on_hold(self.order)


class ResumeOrder(OrderActionHandler):
    """
    Resume an order from 'on_hold' state.
    """
    def is_allowed(self) -> bool:
        return self.order.status == 'on_hold'

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Only orders on hold can be resumed."
            )
        return OrderService.resume_order(self.order)


class AssignWriter(OrderActionHandler):
    """
    Assign a writer to the order.
    """
    def is_allowed(self) -> Order:
        return self.order.status == 'pending'
    
    def perform(self, writer: User) -> Dict[str, Any]:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be in 'pending' state to assign a writer."
            )
        return self.handle(writer)
    
    def handle(self, writer: User) -> Dict[str, Any]:
        """
        Handles the actual assignment of a writer to the order.
        """
        if self.order.writer:
            raise ValueError("Order already has a writer.")
        self.order.writer = writer
        self.order.status = "in_progress"
        self.order.assigned_at = timezone.now()
        self.order.save()
        send_notification(
            writer,
            "New Order Assigned",
            f"You have been assigned Order #{self.order.id}."
        )
        logger.info(f"Writer {writer.id} successfully assigned to order {self.order.id}")
        return {"message": "Writer assigned successfully."}


class OrderReassignmentActionHandler(OrderActionHandler):
    """
    Action handler for processing reassignment of an order.
    """

    def __init__(self, order, requested_by, reason, preferred_writer=None):
        self.order = order
        self.requested_by = requested_by
        self.reason = reason
        self.preferred_writer = preferred_writer

    def perform_action(self):
        """
        Perform the reassignment action: create a reassignment request and process it.
        """

        # Step 1: Create a reassignment request
        try:
            reassignment_request = create_reassignment_request(
                order=self.order,
                requester=self.order.client,  # Assuming the client is requesting
                reason=self.reason,
                requested_by=self.requested_by,
                preferred_writer=self.preferred_writer
            )
        except ValueError as e:
            raise TransitionNotAllowed(str(e))
        except Exception as e:
            raise Exception(f"Failed to create reassignment request: {str(e)}")

        # Step 2: Resolve the reassignment request (this could be based on admin action or other triggers)
        try:
            updated_order = resolve_reassignment_request(
                order_id=self.order.id,
                status='reassigned',
                processed_by=None,  # This can be set to the user processing the reassignment
                fine=0.00,  # If applicable, calculate fine based on your logic
                metadata={'assigned_writer': self.preferred_writer}
            )
        except Exception as e:
            raise Exception(f"Failed to resolve reassignment request: {str(e)}")

        # Step 3: Return the updated order after reassignment
        return updated_order

class CompleteOrder(OrderActionHandler):
    """
    Mark the order as complete.
    """

    def is_allowed(self) -> bool:
        return self.order.status == 'assigned'

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be 'assigned' before it can be completed."
            )
        return OrderService.complete_order(self.order)


class DisputeOrder(OrderActionHandler):
    """
    Mark the order as disputed.
    """

    def is_allowed(self) -> bool:
        return self.order.status in ['assigned', 'revision']

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be in 'assigned' or 'revision' state to dispute."
            )
        return OrderService.dispute_order(self.order)


class ApproveOrder(OrderActionHandler):
    """
    Approve the order once completed.
    """

    def is_allowed(self) -> bool:
        return self.order.status == 'completed'

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be 'completed' before it can be approved."
            )
        return OrderService.approve_order(self.order)


class CancelOrder(OrderActionHandler):
    """
    Cancel the order.
    """

    def is_allowed(self) -> bool:
        return self.order.status not in ['completed', 'archived']

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order cannot be cancelled once it is completed or archived."
            )
        return OrderService.cancel_order(self.order)


class ArchiveOrder(OrderActionHandler):
    """
    Archive the order once completed.
    """

    def is_allowed(self) -> bool:
        return self.order.status == 'completed'

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be 'completed' before it can be archived."
            )
        return OrderService.archive_order(self.order)


class LateOrder(OrderActionHandler):
    """
    Mark the order as late.
    """

    def is_allowed(self) -> bool:
        return self.order.status == 'assigned'

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be marked as late."
            )
        return OrderService.late_order(self.order)


class RevisionOrder(OrderActionHandler):
    """
    Mark the order for revision.
    """

    def is_allowed(self) -> bool:
        return self.order.status == 'assigned'

    def perform(self) -> Order:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be marked for revision."
            )
        return OrderService.revision_order(self.order)


# Revision-specific Actions
class RequestRevisionAction(OrderActionHandler):
    """
    Action to request a revision for an order.
    """

    def __init__(self, order: Order, reason: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(order, *args, **kwargs)
        self.reason = reason

    def execute(self):
        """
        Request a revision for the order.
        """
        if not request_revision(self.order, self.reason):
            raise ValueError(
                "The revision request is not valid for this order."
            )
        return f"Revision requested for order {self.order.id}."

    def handle(self):
        """
        Handle the logic to request a revision.
        """
        user = self.user
        order = self.order

        if order.status != OrderStatus.COMPLETED:
            raise ValueError("Only completed orders can be revised.")

        # Only admins, support, editors, or the client can request a revision
        if not (user.is_staff or getattr(user, 'is_editor', False) or
                order.client == user):
            raise PermissionError("You do not have permission to request a revision.")

        # Time-based check (e.g., 14-day window)
        config = RevisionPolicyConfig.objects.first()
        allowed_days = config.free_revision_days if config else 14  # fallback

        if order.completed_at and (timezone.now() - order.completed_at) > \
                timedelta(days=allowed_days):
            raise ValueError("The revision window has expired.")

        reason = self.data.get("reason")
        if not reason:
            raise ValueError("A reason must be provided for revision.")

        order.status = OrderStatus.REVISION_REQUESTED
        order.save()

        send_notification(
            order.writer,
            "Revision Requested",
            f"A revision has been requested for order #{order.id}."
        )
        return {"message": "Revision request submitted."}


class ProcessRevisionAction(OrderActionHandler):
    """
    Action to process the revision of an order.
    """

    def __init__(self, order: Order, revised_work: Any, *args: Any,
                 **kwargs: Any) -> None:
        super().__init__(order, *args, **kwargs)
        self.revised_work = revised_work

    def execute(self):
        """
        Process the revision for the order.
        """
        if not process_revision(self.order, self.revised_work):
            raise ValueError("Cannot process revision for this order.")
        return f"Revision processed for order {self.order.id}."

    def handle(self):
        """
        Handle the logic to process the revision.
        """
        user = self.user

        if not getattr(user, 'is_writer', False):
            raise PermissionError(
                "Only writers can process revisions."
            )

        if self.order.status != OrderStatus.REVISION_REQUESTED:
            raise ValueError(
                "No revision request found for this order."
            )

        if self.order.writer != user:
            raise PermissionError(
                "You are not assigned to this order."
            )

        self.order.status = OrderStatus.ON_REVISION
        self.order.save()

        send_notification(
            self.order.client, "Revision In Progress",
            f"Your order #{self.order.id} is being revised."
        )
        return {"message": "Revision is now in progress."}


class DenyRevisionAction(OrderActionHandler):
    """
    Action to deny the revision request for an order.
    """

    def __init__(self, order: Order, reason: str, *args: Any,
                 **kwargs: Any) -> None:
        super().__init__(order, *args, **kwargs)
        self.reason = reason

    def execute(self):
        """
        Deny the revision request for the order.
        """
        if not deny_revision(self.order, self.reason):
            raise ValueError("Cannot deny revision for this order.")
        return f"Revision denied for order {self.order.id}."

    def handle(self):
        """
        Handle the logic to deny the revision.
        """
        user = self.user

        if not (user.is_staff or getattr(user, 'is_editor', False)):
            raise PermissionError(
                "Only admin, support, or editors can deny revisions."
            )

        if self.order.status != OrderStatus.REVISION_REQUESTED:
            raise ValueError(
                "No active revision to deny."
            )

        denial_reason = self.data.get("reason")
        if not denial_reason:
            raise ValueError(
                "A reason for denying the revision must be provided."
            )

        self.order.status = OrderStatus.COMPLETED
        self.order.save()

        send_notification(
            self.order.client,
            "Revision Denied",
            f"Your revision request for Order #{self.order.id} was denied."
        )
        return {"message": "Revision request denied."}
    
class UploadFinalWorkAction(OrderActionHandler):
    """
    Action for the writer to upload final deliverables for the order.
    """

    def __init__(self, order: Order, final_file: Any, *args: Any, **kwargs: Any):
        super().__init__(order, *args, **kwargs)
        self.final_file = final_file

    def is_allowed(self) -> bool:
        return (
            self.order.status == OrderStatus.ASSIGNED
            and self.order.writer == self.user
        )

    def perform(self) -> dict:
        if not self.is_allowed():
            raise TransitionNotAllowed(
                "You are not allowed to upload work for this order."
            )

        # Save the final file – this assumes your Order model has a final_work or similar field
        self.order.final_work = self.final_file
        self.order.save()

        send_notification(
            self.order.client,
            "Final Work Uploaded",
            f"Order #{self.order.id} has final work uploaded by your writer."
        )

        return {"message": "Final work uploaded successfully."}
    
class EditOrderInProgress(OrderActionHandler):
    """
    Allows editing of an order only by admin or support if the order is in
    progress.
    """

    def is_allowed(self) -> bool:
        if self.order.status != 'in_progress':
            raise TransitionNotAllowed("Order must be in progress to be edited.")
        
        if self.user.role not in ['admin', 'support']:
            raise TransitionNotAllowed("Only admin or support can edit this order.")
        
        return True

    def perform(self) -> Order:
        """
        Perform the actual edit of the order.
        """
        # Implement logic to edit the order as needed
        self.order.save()
        send_notification(self.order.client, "Order Edited", f"Your order #{self.order.id} has been edited.")
        logger.info(f"Order {self.order.id} has been edited by {self.user.id}.")
        return self.order


class RequestDeadlineExtension(OrderActionHandler):
    """
    Allows a client to request a deadline extension, with a reason or counter
    deadline.
    """

    def __init__(self, order: Order, *args, **kwargs):
        super().__init__(order, *args, **kwargs)
        self.reason = self.data.get('reason')
        self.new_deadline = self.data.get('new_deadline')

    def is_allowed(self) -> bool:
        if self.order.status != 'assigned':
            raise TransitionNotAllowed("Deadline extension can only be requested for assigned orders.")
        if self.user.role != 'client':
            raise TransitionNotAllowed("Only clients can request a deadline extension.")
        if not self.reason:
            raise TransitionNotAllowed("Reason for the extension must be provided.")
        
        return True

    def perform(self) -> Order:
        """
        Perform the deadline extension request.
        """
        self.order.deadline_extension_requested = True
        self.order.deadline_request_reason = self.reason
        self.order.counter_deadline = self.new_deadline
        self.order.save()

        send_notification(
            self.order.writer,
            "Deadline Extension Request",
            f"A deadline extension has been requested for Order #{self.order.id}."
        )
        logger.info(f"Deadline extension requested for Order {self.order.id} by Client {self.user.id}.")
        return self.order
    
    def execute(self):
        """
        Request deadline extension from the client.
        """
        if self.order.status != OrderStatus.IN_PROGRESS:
            raise TransitionNotAllowed("You cannot request a deadline extension now.")

        if not self.is_writer():
            raise PermissionError("Only the Writer can request a deadline extension.")

        self.order.deadline = self.new_deadline
        self.order.save()

        # Notify the admin or support
        send_notification(
            self.order.assigned_writer, "Deadline Extension Requested",
            f"Client has requested a new deadline for Order #{self.order.id}."
        )

        return {"message": "Deadline extension requested."}


class ApproveDeadlineExtension(OrderActionHandler):
    """
    Admin or support approves the deadline extension request.
    """

    def __init__(self, order: Order, new_deadline: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(order, *args, **kwargs)
        self.new_deadline = new_deadline

    def execute(self):
        """
        Approve the deadline extension.
        """
        if not self.is_admin_or_support():
            raise PermissionError("Only admin or support can approve extensions.")

        self.order.deadline = self.new_deadline
        self.order.save()

        send_notification(
            self.order.client, "Deadline Extension Approved",
            f"Your deadline extension request for Order #{self.order.id} has been approved."
        )

        return {"message": "Deadline extension approved."}

class ManageDeadlineExtension(OrderActionHandler):
    """
    Admin or support can manage a deadline extension request (accept, reject,
    or override).
    """

    def __init__(self, order: Order, *args, **kwargs):
        super().__init__(order, *args, **kwargs)
        self.accept_extension = self.data.get('accept_extension')  # True or False
        self.override_deadline = self.data.get('override_deadline')  # New date

    def is_allowed(self) -> bool:
        if self.user.role not in ['admin', 'support']:
            raise TransitionNotAllowed("Only admin or support can manage the deadline extension.")
        if not self.order.deadline_extension_requested:
            raise TransitionNotAllowed("No deadline extension request to manage.")
        
        return True

    def perform(self) -> Order:
        """
        Accept, reject, or override the deadline extension request.
        """
        if self.accept_extension:
            self.order.deadline = self.override_deadline if self.override_deadline else self.order.deadline
            self.order.deadline_extension_requested = False
            self.order.save()
            send_notification(
                self.order.client,
                "Deadline Extension Accepted",
                f"Your deadline extension request for Order #{self.order.id} has been accepted."
            )
            logger.info(f"Deadline extension accepted for Order {self.order.id}.")
        else:
            self.order.deadline_extension_requested = False
            self.order.save()
            send_notification(
                self.order.client,
                "Deadline Extension Rejected",
                f"Your deadline extension request for Order #{self.order.id} has been rejected."
            )
            logger.info(f"Deadline extension rejected for Order {self.order.id}.")
        
        return self.order


class AddExtraPages(OrderActionHandler):
    """
    Allows the client to request additional pages for an order.
    """

    def __init__(self, order: Order, *args, **kwargs):
        super().__init__(order, *args, **kwargs)
        self.extra_pages = self.data.get('extra_pages')  # Number of extra pages

    def is_allowed(self) -> bool:
        if self.order.status != 'assigned':
            raise TransitionNotAllowed(
                "Extra pages can only be added to orders in 'assigned' state."
            )
        if self.user.role != 'client':
            raise TransitionNotAllowed(
                "Only clients can request extra pages."
            )
        
        if not self.extra_pages or self.extra_pages <= 0:
            raise TransitionNotAllowed(
                "A positive number of extra pages must be specified."
            )
        
        return True

    def perform(self) -> Order:
        """
        Perform the addition of extra pages to the order.
        """
        self.order.extra_pages = self.extra_pages
        self.order.save()

        send_notification(
            self.order.writer,
            "Extra Pages Added",
            f"Extra pages have been added to Order #{self.order.id}."
        )
        logger.info(f"Extra pages added to Order {self.order.id} by Client {self.user.id}.")
        return self.order


class RequestAdditionalServices(OrderActionHandler):
    """
    Allows the client to request additional services for the order (e.g.,
    plagiarism report, smart paper).
    """

    def __init__(self, order: Order, *args, **kwargs):
        super().__init__(order, *args, **kwargs)
        self.services = self.data.get('services', [])

    def is_allowed(self) -> bool:
        if self.order.status != 'assigned':
            raise TransitionNotAllowed("Additional services can only be requested for assigned orders.")
        if self.user.role != 'client':
            raise TransitionNotAllowed("Only clients can request additional services.")
        
        return True

    def perform(self) -> Order:
        """
        Add requested services to the order.
        """
        for service in self.services:
            # Assuming the services are predefined in the system (e.g., plagiarism report)
            self.order.additional_services.append(service)
        
        self.order.save()

        send_notification(
            self.order.writer,
            "Additional Services Requested",
            f"Additional services have been requested for Order #{self.order.id}."
        )
        logger.info(
            f"Additional services requested for Order {self.order.id} by Client {self.user.id}."
        )
        return self.order
    

