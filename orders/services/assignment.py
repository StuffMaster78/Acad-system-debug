from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from orders.models import Order
from notifications_system.utils import send_notification 
from orders.services.order_access_service import OrderAccessService
from django.core.exceptions import PermissionDenied
from orders.models import WriterReassignmentLog

User = get_user_model()

class OrderAssignmentService:
    """
    Service to handle assignment and unassignment of writers to orders.
    """

    def __init__(self, order: Order):
        """
        Initializes the OrderAssignmentService.

        Args:
            order (Order): The order to operate on.
        """
        self.order = order

    @transaction.atomic
    def assign_writer(self, writer_id: int, reason) -> Order:
        """
        Assigns a writer to an order and updates its status.

        Args:
            writer_id (int): The ID of the writer to assign.

        Returns:
            Order: The updated order with an assigned writer.
        """
        if self.order.assigned_writer:
            raise ValidationError("Order is already assigned to a writer.")

        try:
            writer = User.objects.get(
                id=writer_id,
                role="writer",
                is_active=True
            )
        except User.DoesNotExist:
            raise ObjectDoesNotExist(
                f"Writer with ID {writer_id} does not exist or is not active."
            )

        can_assign = OrderAccessService.can_be_assigned(
            writer=writer,
            order=self.order,
            by_admin=self.actor.is_staff
        )

        if not can_assign:
            raise PermissionDenied(
                "Writer level too low for this order."
            )
        
        old_writer = self.order.assigned_writer
        is_reassignment = bool(old_writer and old_writer != writer)

        self.order.assigned_writer = writer
        self.order.status = "in_progress"
        self.order.save()

        if is_reassignment:
            self._notify_reassignment(old_writer, writer, "Reassignment by admin")
        else:
            self._notify_assignment(writer)

        if is_reassignment:
            WriterReassignmentLog.objects.create(
                order=self.order,
                previous_writer=old_writer,
                new_writer=writer,
                reassigned_by=self.actor,
                reason=reason
            )

        send_notification(
            writer,
            "New Order Assigned",
            f"You've been assigned to Order #{self.order.id}."
        )

        send_notification(
            self.order.client,
            "Writer Assigned",
            f"A writer has been assigned to your Order #{self.order.id}."
        )

        return self.order


    @transaction.atomic
    def unassign_writer(self) -> Order:
        """
        Unassigns the current writer from an order and sets it back to available.

        Args:
            order (Order): The order to update.

        Returns:
            Order: The updated order with no assigned writer.
        """
        if not self.order.assigned_writer:
            raise ValidationError("Order is not currently assigned to any writer.")

        writer = self.order.assigned_writer
        self.order.assigned_writer = None
        self.order.status = "available"
        self.order.save()

        send_notification(
            writer,
            "Order Unassigned",
            f"You've been unassigned from Order #{self.order.id}."
        )
        send_notification(
            self.order.client,
            "Writer Unassigned",
            f"The writer was unassigned from your Order #{self.order.id} and it's now available again."
        )

        return self.order
    

    def _notify_assignment(self, writer):
        send_notification(
            writer,
            "New Order Assigned",
            f"You've been assigned Order #{self.order.id}."
        )

        send_notification(
            self.order.client,
            "Writer Assigned",
            f"A writer has been assigned to Order #{self.order.id}."
        )

    def _notify_reassignment(self, old_writer, new_writer, reason):
        send_notification(
            old_writer,
            "Order Reassigned",
            f"Order #{self.order.id} has been reassigned to another writer. "
            f"{'Reason: ' + reason if reason else ''}"
        )

        send_notification(
            new_writer,
            "Order Assigned (Reassignment)",
            f"You've been assigned to Order #{self.order.id}, "
            f"previously handled by {old_writer.get_full_name()}."
        )

        send_notification(
            self.order.client,
            "Writer Reassigned",
            f"Order #{self.order.id} has a new writer assigned."
        )