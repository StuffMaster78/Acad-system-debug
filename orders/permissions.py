from rest_framework.permissions import BasePermission
from users.models import User



class IsAuthenticated(BasePermission):
    """
    Custom permission to check if the user is authenticated.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsSuperadminOnly(BasePermission):
    """
    Allows access only to superadmins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == User.SUPERADMIN


class IsAdminOrSuperAdmin(BasePermission):
    """
    Custom permission to allow admins and superadmins to view or modify any order.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.ADMIN, User.SUPERADMIN]


class IsSupportOrAdmin(BasePermission):
    """
    Allow only support or admin staff.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.ADMIN, User.SUPERADMIN, User.SUPPORT]


class IsAssignedWriter(BasePermission):
    """
    Allow only the writer assigned to this order.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == User.WRITER


class IsClientWhoOwnsOrder(BasePermission):
    """
    Allow only the client who placed the order.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.client


class CanRequestReassignment(BasePermission):
    """
    Custom permission to allow clients, writers, and admins to request reassignment.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.WRITER:
            return obj.writer == request.user  # Writer must be assigned to the order
        elif request.user.role == User.CLIENT:
            return obj.client == request.user  # Client must own the order
        return request.user.role in [User.ADMIN, User.SUPERADMIN]  # Admins can request reassignment for any order


class CanChangeOrderStatus(BasePermission):
    """
    Custom permission to allow clients to approve/cancel their own orders,
    or allow admins to do so for any order.
    """
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user or request.user.role in [User.ADMIN, User.SUPERADMIN]  # Clients and admins can change order status


class IsAssignedWriterOrAdmin(BasePermission):
    """
    Custom permission to allow the assigned writer or an admin to complete the order.
    """
    def has_object_permission(self, request, view, obj):
        return obj.writer == request.user or request.user.role in [User.ADMIN, User.SUPERADMIN]


class CanExecuteOrderAction(BasePermission):
    """
    Custom permission to allow only admins or superadmins to force execute order actions.
    """
    def has_permission(self, request, view):
        return request.user.role in [User.ADMIN, User.SUPERADMIN]  # Admins and superadmins can execute any action


class CanSubmitDispute(BasePermission):
    """
    Custom permission to allow clients or writers to submit a dispute.
    """
    def has_permission(self, request, view):
        return request.user.role in [User.CLIENT, User.WRITER]  # Both writers and clients can submit disputes


class CanSubmitWriterResponse(BasePermission):
    """
    Custom permission to allow the assigned writer to submit a response to a dispute.
    """
    def has_permission(self, request, view):
        dispute = view.get_object()  # Fetch the dispute object
        return dispute.writer == request.user  # Only the assigned writer can respond to the dispute


class IsSuperadminOrAdminForDisputeResolution(BasePermission):
    """
    Custom permission to allow superadmins or admins to resolve disputes.
    """
    def has_permission(self, request, view):
        return request.user.role in [User.ADMIN, User.SUPERADMIN]  # Only admins or superadmins can resolve disputes