from typing import Any, Dict
from .base import OrderActionHandler
from orders.models import Order
from orders.services.order_service import OrderService
from django.core.exceptions import ValidationError
from services.revisions import request_revision, process_revision, deny_revision
from django_fsm import TransitionNotAllowed  # type: ignore
from notifications_system.utils import send_website_mail, send_notification
from order_configs.models import RevisionPolicyConfig
from datetime import timedelta
from django.utils import timezone
from users.models import User
from orders.models import OrderStatus

class OrderActionHandler:
    """
    Base class for handling order actions.
    Each order action (e.g., transition, assign, complete) is a subclass of this.
    """
    def __init__(self, order: Order, *args, **kwargs):
        self.order = order

    def is_allowed(order: Order) -> bool:
        """
        Determines whether the action can be performed on the given order.

        :param order: The order object.
        :return: bool indicating if the action is allowed.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def perform(order: Order, *args, **kwargs):
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
        self.order.save()
        send_notification(
            writer,
            "New Order Assigned",
            f"You have been assigned Order #{self.order.id}."
        )
        return {"message": "Writer assigned successfully."}


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
            raise ValueError("The revision request is not valid for this order.")
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
        allowed_days = RevisionPolicyConfig.free_revision_days
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
            raise PermissionError("Only writers can process revisions.")

        if self.order.status != OrderStatus.REVISION_REQUESTED:
            raise ValueError("No revision request found for this order.")

        if self.order.writer != user:
            raise PermissionError("You are not assigned to this order.")

        self.order.status = OrderStatus.IN_PROGRESS
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
            raise PermissionError("Only admin, support, or editors can deny revisions.")

        if self.order.status != OrderStatus.REVISION_REQUESTED:
            raise ValueError("No active revision to deny.")

        denial_reason = self.data.get("reason")
        if not denial_reason:
            raise ValueError("A reason for denying the revision must be provided.")

        self.order.status = OrderStatus.COMPLETED
        self.order.save()

        send_notification(
            self.order.client,
            "Revision Denied",
            f"Your revision request for Order #{self.order.id} was denied."
        )
        return {"message": "Revision request denied."}