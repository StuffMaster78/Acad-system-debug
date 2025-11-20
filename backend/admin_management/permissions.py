from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allows access to both Admins and Superadmins."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "superadmin"]
        )


class IsSuperAdmin(BasePermission):
    """Allows access only to Superadmins."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == "superadmin"
        )


class CanManageUsers(BasePermission):
    """Allows access only to Admins who have 'can_manage_users' permission."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "superadmin"] and 
            request.user.admin_profile.can_manage_users
        )


class CanManageOrders(BasePermission):
    """Allows access only to Admins who have 'can_handle_orders' permission."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "superadmin"] and 
            request.user.admin_profile.can_handle_orders
        )


class CanManagePayouts(BasePermission):
    """Allows access only to Admins who have 'can_manage_payouts' permission."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "superadmin"] and 
            request.user.admin_profile.can_manage_payouts
        )


class CanResolveDisputes(BasePermission):
    """Allows access only to Admins who have 'can_resolve_disputes' permission."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "superadmin"] and 
            request.user.admin_profile.can_resolve_disputes
        )


class CanBlacklistUsers(BasePermission):
    """Allows only Superadmins to blacklist users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == "superadmin"
        )


class CanManageProbation(BasePermission):
    """Allows access only to Admins who have 'can_suspend_users' permission."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "superadmin"] and 
            request.user.admin_profile.can_suspend_users
        )