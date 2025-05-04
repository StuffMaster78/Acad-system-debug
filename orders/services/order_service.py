from django.db import transaction
from django_fsm import TransitionNotAllowed  # type: ignore
from orders.models import Order, STATUS_CHOICES


def save_order(order: Order):
    """
    Helper function to save the order.

    Args:
        order (Order): The order to save.
    """
    order.save()


class OrderService:
    """
    Service class to handle the order lifecycle and state transitions.
    """

    @staticmethod
    @transaction.atomic
    def transition_to_pending(order: Order):
        """
        Transition order to 'pending' state if allowed.

        :param order: The order to transition.
        :raises: TransitionNotAllowed if order is not in a valid state for
                'pending'.
        """
        if order.status not in ['unpaid', 'available']:
            raise TransitionNotAllowed(
                "Order cannot be moved to 'pending' from the current status."
            )

        order.status = 'pending'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def put_on_hold(order: Order):
        """
        Puts the order on hold.

        :param order: The order to put on hold.
        :raises: TransitionNotAllowed if order is not in 'assigned' state.
        """
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be put on hold."
            )

        order.status = 'on_hold'
        save_order(order)
        return order
    
    @staticmethod
    @transaction.atomic
    def resume_order(order: Order):
        """
        Resume an order from on hold status.

        :param order: The order to resume.
        :raises: TransitionNotAllowed if order is not in 'on_hold' state.
        """
        if order.status != 'on_hold':
            raise TransitionNotAllowed(
                "Only orders on hold can be resumed."
            )

        order.status = 'assigned'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def assign_writer(order: Order, writer):
        """
        Assign a writer to the order.

        :param order: The order to assign.
        :param writer: The writer to assign.
        :raises: TransitionNotAllowed if order is not in 'pending' state.
        """
        if order.status != 'pending':
            raise TransitionNotAllowed(
                "Order must be in 'pending' state to assign a writer."
            )

        order.status = 'assigned'
        order.writer = writer  # Assuming there is a `writer` field on the `Order`.
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def complete_order(
        order: Order,
        completed_by=None,
        completion_notes=None
    ):
        """
        Mark the order as complete.

        :param order: The order to complete.
        :raises: TransitionNotAllowed if order is not in 'assigned' state.
        """
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' before it can be completed."
            )
        
         # If an admin/support is completing the order manually, record who did it
        if completed_by:
            order.completed_by = completed_by
            order.completion_notes = (
                completion_notes or "Completed manually by support/admin."
            )

        order.status = 'completed'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def dispute_order(order: Order):
        """
        Mark the order as disputed.

        :param order: The order to dispute.
        :raises: TransitionNotAllowed if order is not in 'assigned' or
                 'revision' state.
        """
        if order.status not in ['assigned', 'revision']:
            raise TransitionNotAllowed(
                "Order must be in 'assigned' or 'revision' state to dispute."
            )

        order.status = 'disputed'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def approve_order(order: Order):
        """
        Approve the order once completed.

        :param order: The order to approve.
        :raises: TransitionNotAllowed if order is not in 'completed' state.
        """
        if order.status != 'completed':
            raise TransitionNotAllowed(
                "Order must be 'completed' before it can be approved."
            )

        order.status = 'approved'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order):
        """
        Cancel the order.

        :param order: The order to cancel.
        :raises: TransitionNotAllowed if order is in 'completed' or 'archived'
                 state.
        """
        if order.status in ['completed', 'archived']:
            raise TransitionNotAllowed(
                "Order cannot be cancelled once it is completed or archived."
            )

        order.status = 'cancelled'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def archive_order(order: Order):
        """
        Archive the order once completed.

        :param order: The order to archive.
        :raises: TransitionNotAllowed if order is not in 'completed' state.
        """
        if order.status != 'completed':
            raise TransitionNotAllowed(
                "Order must be 'completed' before it can be archived."
            )

        order.status = 'archived'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def late_order(order: Order):
        """
        Mark the order as late.

        :param order: The order to mark as late.
        :raises: TransitionNotAllowed if order is not in 'assigned' state.
        """
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be marked as late."
            )

        order.status = 'late'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def revision_order(order: Order):
        """
        Mark the order for revision.

        :param order: The order to mark for revision.
        :raises: TransitionNotAllowed if order is not in 'assigned' state.
        """
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be marked for revision."
            )

        order.status = 'revision'
        save_order(order)
        return order