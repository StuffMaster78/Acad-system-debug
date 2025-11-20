from rest_framework.permissions import BasePermission


class IsAdminUserOrReadOnly(BasePermission):
    """
    Allows full access to admin users and read-only access to others.
    """

    def has_permission(self, request, view):
        # Allow read-only actions (GET, HEAD, OPTIONS) for everyone
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # Full access for admin users only
        return request.user.is_authenticated and request.user.is_staff


class IsSuperAdmin(BasePermission):
    """
    Custom permission to allow access only to superadmins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superadmin


class IsAdminOfWebsite(BasePermission):
    """
    Allows access to admins who belong to the same website as the resource.
    """

    def has_permission(self, request, view):
        # Only allow access to authenticated users
        if not request.user.is_authenticated or not request.user.is_staff:
            return False

        # Check if the user has access to the website resource
        website = getattr(request.user, 'website', None)
        if not website:
            return False

        # If the resource is website-specific, ensure user belongs to the same website
        if hasattr(view, 'get_object'):
            obj = view.get_object()
            return getattr(obj, 'website', None) == website

        # Default to allowing access if no specific object is tied
        return True