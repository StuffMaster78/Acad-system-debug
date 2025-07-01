from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == "superadmin"
    
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
            if not thread.is_active and not thread.admin_override and request.user.profile.role in ["client", "writer"]:
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
        return (
            user.profile.role in ["admin", "superadmin"]
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
        return user.profile.role in allowed_roles


def can_start_thread(user, order) -> bool:
    """
    Check whether a user is allowed to start a communication thread for an order.
    """
    role = getattr(user.profile, "role", None)
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
    """
    order = getattr(thread, "order", None)
    role = getattr(user.profile, "role", None)

    if not thread.is_active and not thread.admin_override:
        return False

    if order.status in {"archived", "cancelled"}:
        return thread.admin_override

    if getattr(order, "is_special", False):
        return thread.admin_override

    if getattr(order, "is_class_order", False):
        return role in {"admin", "support", "instructor"}

    return True


def can_view_thread(user, thread) -> bool:
    """
    Check whether a user can view a given thread.
    """
    if user.is_staff:
        return True  # Admins can always view

    if user in thread.participants.all():
        return True  # Participants can view

    # Additional checks for special cases
    order = getattr(thread, "order", None)
    if order and order.is_special and user.profile.role in {"admin", "support"}:
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
    if getattr(message, "order", None) and message.order.is_special and user.profile.role in {"admin", "support"}:
        return True

    return False  # Default deny


def can_delete_message(user, message) -> bool:
    """
    Check whether a user can delete a given message.
    """
    if user.is_staff:
        return True  # Admins can delete any message

    if message.sender == user:
        return True  # Owners can delete their own messages

    # Additional checks for special cases
    if getattr(message, "order", None) and message.order.is_special and user.profile.role in {"admin", "support"}:
        return True

    return False  # Default deny


def can_reply_to_thread(user, thread) -> bool:
    """
    Check whether a user can reply to a given thread.
    """
    if user.is_staff:
        return True  # Admins can reply to any thread

    if user in thread.participants.all():
        return True  # Participants can reply

    # Additional checks for special cases
    order = getattr(thread, "order", None)
    if order and order.is_special and user.profile.role in {"admin", "support"}:
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
    if getattr(message, "order", None) and message.order.is_special and user.profile.role in {"admin", "support"}:
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