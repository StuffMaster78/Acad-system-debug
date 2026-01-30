from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == "superadmin"
    
class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a message or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:  # Admins have full access
            return True
        return obj.sender == request.user  # Owners can only edit their own messages


class CanSendOrderMessage(permissions.BasePermission):
    """
    Restricts messaging if the order is archived and no admin override is set.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            thread = view.get_object()
            user_role = getattr(request.user, 'role', None)
            if not thread.is_active and not thread.admin_override and user_role in ["client", "writer"]:
                return False
        return True


class IsThreadParticipant(permissions.BasePermission):
    """
    ✅ Allow only thread participants to access or modify.
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


class IsSenderOrRecipient(permissions.BasePermission):
    """
    ✅ Allow only sender or recipient of a message.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.sender or request.user == obj.recipient


class IsAdminOrOwner(permissions.BasePermission):
    """
    ✅ Allow access if user is admin or the owner of the object.
    Assumes `obj.sender` or `obj.user` ownership pattern.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        user_role = getattr(user, 'role', None)
        return (
            user_role in ["admin", "superadmin"]
            or getattr(obj, "sender", None) == user
            or getattr(obj, "user", None) == user
        )


class CanSendCommunicationMessage(permissions.BasePermission):
    """
    ✅ Check if the user has permission to send messages.
    This can evolve into more complex org-specific policies.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Basic policy: allow if user has a valid role
        allowed_roles = ["client", "writer", "editor", "admin", "superadmin"]
        user_role = getattr(user, 'role', None)
        return user_role in allowed_roles


def can_start_thread(user, order) -> bool:
    """
    Check whether a user is allowed to start a communication thread for an order.
    """
    role = getattr(user, "role", None)
    status = getattr(order, "status", None)

    if status in {"archived", "cancelled"}:
        return False

    if getattr(order, "is_special", False):
        return False

    if getattr(order, "is_class_order", False):
        return role in {"admin", "support", "instructor"}

    return True  # Default allow


def can_send_message(user, thread) -> bool:
    """
    Check whether a user can send a message in a given thread.
    Allows all users with access to the order to send messages.
    """
    order = getattr(thread, "order", None)
    special_order = getattr(thread, "special_order", None)
    role = getattr(user, "role", None)

    if not thread.is_active and not thread.admin_override:
        return False

    # If no order or special order, check if user is a participant
    if not order and not special_order:
        return user in thread.participants.all()

    # Check if user has access to the order
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

    if not has_order_access and special_order:
        has_order_access = (
            special_order.client == user or
            special_order.writer == user or
            role in {"admin", "superadmin", "editor", "support"} or
            user in thread.participants.all()
        )

    if not has_order_access:
        return False

    # Role-specific fencing for order threads
    if role == "writer":
        if user in thread.participants.all():
            pass
        elif order.assigned_writer == user and (
            thread.sender_role == "writer" or thread.recipient_role == "writer"
        ):
            pass
        elif special_order and special_order.writer == user and (
            thread.sender_role == "writer" or thread.recipient_role == "writer"
        ):
            pass
        else:
            return False

    if role == "client":
        if user in thread.participants.all():
            pass
        elif order.client == user and (
            thread.sender_role == "client" or thread.recipient_role == "client"
        ):
            pass
        elif special_order and special_order.client == user and (
            thread.sender_role == "client" or thread.recipient_role == "client"
        ):
            pass
        else:
            return False

    # Check order status restrictions
    if order and order.status in {"archived", "cancelled"}:
        return thread.admin_override

    if getattr(order, "is_class_order", False):
        return role in {"admin", "support", "instructor"}

    return True


def can_view_thread(user, thread) -> bool:
    """
    Check whether a user can view a given thread.
    Allows all users with access to the order to view threads.
    """
    if user.is_staff:
        return True  # Admins can always view

    # Check if user is a participant
    if user in thread.participants.all():
        return True

    # Check if user has access to the order or special order
    order = getattr(thread, "order", None)
    special_order = getattr(thread, "special_order", None)
    if order:
        role = getattr(user, "role", None)

        # Staff roles have access
        if role in {"admin", "superadmin", "editor", "support"}:
            return True

        # Client who placed the order (client-involved threads only)
        if order.client == user and (
            thread.sender_role == "client" or thread.recipient_role == "client"
        ):
            return True

        # Writer assigned to the order (writer-involved threads only)
        if order.assigned_writer == user and (
            thread.sender_role == "writer" or thread.recipient_role == "writer"
        ):
            return True

    if special_order:
        role = getattr(user, "role", None)
        if role in {"admin", "superadmin", "editor", "support"}:
            return True
        if special_order.client == user and (
            thread.sender_role == "client" or thread.recipient_role == "client"
        ):
            return True
        if special_order.writer == user and (
            thread.sender_role == "writer" or thread.recipient_role == "writer"
        ):
            return True

    return False  # Default deny


def can_edit_message(user, message) -> bool:
    """
    Check whether a user can edit a given message.
    """
    if user.is_staff:
        return True  # Admins can edit any message

    if message.sender == user:
        return True  # Owners can edit their own messages

    # Additional checks for special cases
    user_role = getattr(user, "role", None)
    thread = getattr(message, "thread", None)
    special_order = getattr(thread, "special_order", None) if thread else None
    if special_order and user_role in {"admin", "support", "superadmin"}:
        return True

    return False  # Default deny


def can_delete_message(user, message) -> bool:
    """
    Check whether a user can delete a given message.
    Only admin/superadmin can delete messages. Clients and writers cannot delete.
    """
    role = getattr(user, "role", None)
    
    # Only admin and superadmin can delete messages
    if role in {"admin", "superadmin"}:
        return True
    
    # Clients and writers cannot delete messages (even their own)
    return False


def can_reply_to_thread(user, thread) -> bool:
    """
    Check whether a user can reply to a given thread.
    Allows all users with access to the order to reply.
    """
    if user.is_staff:
        return True  # Admins can reply to any thread

    # Check if user is a participant
    if user in thread.participants.all():
        return True

    # Check if user has access to the order
    order = getattr(thread, "order", None)
    if order:
        role = getattr(user, "role", None)
        
        # Client who placed the order
        if order.client == user:
            return True
        # Writer assigned to the order
        if order.assigned_writer == user:
            return True
        # Staff roles have access
        if role in {"admin", "superadmin", "editor", "support"}:
            return True
        # Special orders - only admin/support
        if order.is_special and role in {"admin", "support"}:
            return True

    return False  # Default deny

def can_view_message(user, message) -> bool:
    """
    Check whether a user can view a given message.
    """
    if user.is_staff:
        return True  # Admins can view any message

    if message.sender == user or message.recipient == user:
        return True  # Owners can view their own messages

    # Additional checks for special cases
    user_role = getattr(user, "role", None)
    if getattr(message, "order", None) and message.order.is_special and user_role in {"admin", "support"}:
        return True

    return False  # Default deny


def can_manage_thread(user, thread) -> bool:
    """
    Check whether a user can manage (view, edit, delete) a given thread.
    """
    return (
        can_view_thread(user, thread)
        and (user.is_staff or user in thread.participants.all())
    )


def can_manage_message(user, message) -> bool:
    """    Check whether a user can manage (view, edit, delete) a given message.
    """
    return (
        can_view_message(user, message)
        and (user.is_staff or message.sender == user or message.recipient == user)
    )


def can_manage_communication_messages(user, order) -> bool:
    """    Check whether a user can manage (view, edit, delete) messages related to an order.
    """
    if user.is_staff:
        return True  # Admins can manage any messages

    # Check if the user is a participant in any thread related to the order
    threads = order.threads.all()
    return any(can_manage_thread(user, thread) for thread in threads)