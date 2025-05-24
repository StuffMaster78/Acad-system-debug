from rest_framework.permissions import BasePermission
from django.utils.timezone import now

from users.models import User
from authentication.constants import ROLE_HIERARCHY
from authentication.models import AuditLog


class IsAuthenticated(BasePermission):
    """
    Custom permission to check if the user is authenticated.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


# === Admin + Role-based Access ===

class IsSuperadminOnly(BasePermission):
    """
    Allows access only to superadmins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == User.SUPERADMIN


class IsAdminOrSuperAdmin(BasePermission):
    """
    Allow admins and superadmins to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.ADMIN, User.SUPERADMIN
        ]


class IsSupportOrAdmin(BasePermission):
    """
    Allow support, admins, or superadmins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.SUPPORT, User.ADMIN, User.SUPERADMIN
        ]


# === Object-Level Permissions ===

class IsAssignedWriter(BasePermission):
    """
    Allow only the writer assigned to this order.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.role == User.WRITER
            and obj.writer == request.user
        )


class IsClientWhoOwnsOrder(BasePermission):
    """
    Allow only the client who placed the order.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.client


class CanRequestReassignment(BasePermission):
    """
    Allow clients, writers, and admins to request reassignment.
    """
    def has_object_permission(self, request, view, obj):
        role = request.user.role
        if role == User.WRITER:
            return obj.writer == request.user
        if role == User.CLIENT:
            return obj.client == request.user
        return role in [User.ADMIN, User.SUPERADMIN]


class CanChangeOrderStatus(BasePermission):
    """
    Allow clients to approve/cancel their own orders,
    or allow admins to do so for any order.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.client or request.user.role in [
            User.ADMIN, User.SUPERADMIN
        ]


class IsAssignedWriterOrAdmin(BasePermission):
    """
    Allow the assigned writer or an admin to act.
    """
    def has_object_permission(self, request, view, obj):
        return obj.writer == request.user or request.user.role in [
            User.ADMIN, User.SUPERADMIN
        ]


# === Dispute Permissions ===

class CanSubmitDispute(BasePermission):
    """
    Allow clients or writers to submit a dispute.
    """
    def has_permission(self, request, view):
        return request.user.role in [User.CLIENT, User.WRITER]


class CanSubmitWriterResponse(BasePermission):
    """
    Allow the assigned writer to submit a response to a dispute.
    """
    def has_permission(self, request, view):
        dispute = view.get_object()
        return dispute.writer == request.user


class IsSuperadminOrAdminForDisputeResolution(BasePermission):
    """
    Allow superadmins or admins to resolve disputes.
    """
    def has_permission(self, request, view):
        return request.user.role in [User.ADMIN, User.SUPERADMIN]


# === Order Action Permission (Generic + Logged) ===

class CanExecuteOrderAction(BasePermission):
    """
    Allow only admins or superadmins to force execute order actions.
    """
    def has_permission(self, request, view):
        return request.user.role in [User.ADMIN, User.SUPERADMIN]


class OrderActionPermission(BasePermission):
    """
    Grants permission based on user role and requested action.
    Logs denied attempts for audit purposes.
    """

    ACTION_ROLE_MAP = {
        'approve_order': ['admin', 'superadmin'],
        'cancel_order': ['support', 'admin', 'superadmin'],
        'hold_order': ['support', 'admin'],
        'resume_order': ['support', 'admin'],
        'complete_order': ['admin', 'superadmin'],
        'rate_order': ['client'],
        'review_order': ['client'],
        'archive_order': ['admin', 'superadmin'],
        'reopen_order': ['admin', 'superadmin'],
        'mark_critical': ['support', 'admin'],
        'apply_discount': ['admin', 'superadmin'],
    }

    def has_permission(self, request, view):
        user = request.user
        action_name = request.data.get('action_name')
        allowed_roles = self.ACTION_ROLE_MAP.get(action_name, [])
        user_role = getattr(user, 'role', None)

        if user_role is None or action_name is None:
            self._log_denial(user, action_name, "Missing role or action_name")
            return False

        if any(
            ROLE_HIERARCHY.get(user_role, -1) >= ROLE_HIERARCHY.get(role, -1)
            for role in allowed_roles
        ):
            return True

        self._log_denial(user, action_name, "Role not authorized")
        return False

    def _log_denial(self, user, action_name, reason):
        AuditLog.objects.create(
            user=user,
            action=f"DENIED: {action_name}",
            timestamp=now(),
            metadata={"reason": reason}
        )