from django.core.exceptions import PermissionDenied
from communications.permissions import (
    can_send_message, can_start_thread
)
class CommunicationGuardService:
    """Service to manage communication permissions."""
    @staticmethod
    def can_start_thread(user, order):
        return can_start_thread(user, order)

    @staticmethod
    def can_send_message(user, thread):
        return can_send_message(user, thread)

    @staticmethod
    def assert_can_send_message(user, thread):
        """
        Enforce messaging restrictions based on thread and order rules.

        Args:
            user (User): The user trying to send a message.
            thread (CommunicationThread): The thread to send to.

        Raises:
            PermissionDenied: If sending is disallowed.
        """
        # Handle class bundle threads (thread_type='class_bundle')
        if thread.thread_type == 'class_bundle':
            # Class bundle threads are handled separately
            # Check if thread is active
            if not thread.is_active and not thread.admin_override:
                raise PermissionDenied("This thread is locked.")
            return  # Allow messaging for class bundles if thread is active
        
        order = getattr(thread, "order", None)

        if not order:
            raise PermissionDenied("This thread is not tied to an order.")

        # Disallow communication on archived orders
        if order.status == "archived":
            raise PermissionDenied("Cannot message on archived orders.")

        # Block special/private class orders if needed
        if getattr(order, "is_special", False):
            raise PermissionDenied("Messaging is blocked for special orders.")

        if getattr(order, "is_class", False):
            raise PermissionDenied("Messaging is blocked for classes.")

        if not thread.is_active and not thread.admin_override:
            raise PermissionDenied("This thread is locked.")

    @staticmethod
    def assert_can_start_thread(user, order):
        if not can_start_thread(user, order):
            raise PermissionError("You cannot create a thread on this order.")
