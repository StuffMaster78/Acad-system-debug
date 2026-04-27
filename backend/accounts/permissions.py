from rest_framework.permissions import BasePermission
from accounts.selectors.account_role_selector import AccountRoleSelector


class HasRolePermission(BasePermission):
    """Generic permission to check if user has a role."""

    required_roles: list[str] = []

    def has_permission(self, request, view):  # pyright: ignore[reportIncompatibleMethodOverride]
        user = request.user
        website = getattr(request, "website", None)

        if not user or not user.is_authenticated:
            return False
        
        if not website:
            return False
        
        account_profile = getattr(request, "account_profile", None)

        if not account_profile:
            return False
        
        return any(
            AccountRoleSelector.has_role(
                account_profile=account_profile,
                role_key=role,
            )
            for role in self.required_roles
        )
    

# Specialized Roles

class IsSuperAdminUserRole(HasRolePermission):
    required_roles = ["superadmin"]

class IsAdminUserRole(HasRolePermission):
    required_roles = ["admin", "super_admin"]

class IsAdminOrSuperAdminRole(HasRolePermission):
    required_roles =["admin", "super_admin"]

class IsWriterUserRole(HasRolePermission):
    required_roles = ["writer"]

class IsStaffUserRole(HasRolePermission):
    required_roles = ["admin", "editor", "support"]

class IsClientUserRole(HasRolePermission):
    required_roles = ["client"]