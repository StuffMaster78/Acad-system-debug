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
        Allows all users with access to the order to send messages.

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
            # If no order, check if user is a participant
            if user not in thread.participants.all():
                raise PermissionDenied("You do not have access to this thread.")
            if not thread.is_active and not thread.admin_override:
                raise PermissionDenied("This thread is locked.")
            return

        # Check if user has access to the order
        role = getattr(user, "role", None)
        has_order_access = False
        
        # Client who placed the order
        if order.client == user:
            has_order_access = True
        # Writer assigned to the order
        elif order.assigned_writer == user:
            has_order_access = True
        # Staff roles (admin, superadmin, editor, support) have access
        elif role in {"admin", "superadmin", "editor", "support"}:
            has_order_access = True
        # User is already a participant
        elif user in thread.participants.all():
            has_order_access = True

        if not has_order_access:
            raise PermissionDenied("You do not have access to this order.")

        # Disallow communication on archived orders (unless admin override)
        if order.status == "archived" and not thread.admin_override:
            raise PermissionDenied("Cannot message on archived orders.")

        # Block special/private class orders if needed (unless admin override)
        if getattr(order, "is_special", False) and not thread.admin_override:
            raise PermissionDenied("Messaging is blocked for special orders.")

        if getattr(order, "is_class", False) and not thread.admin_override:
            raise PermissionDenied("Messaging is blocked for classes.")

        if not thread.is_active and not thread.admin_override:
            raise PermissionDenied("This thread is locked.")

    @staticmethod
    def assert_can_start_thread(user, order):
        if not can_start_thread(user, order):
            raise PermissionDenied("You cannot create a thread on this order.")
