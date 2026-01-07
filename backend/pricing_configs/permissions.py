from rest_framework.permissions import BasePermission


class IsAdminUserOrReadOnly(BasePermission):
    """
    Allows full access to admin users and read-only access to authenticated users.
    """

    def has_permission(self, request, view):
        # Allow read-only actions (GET, HEAD, OPTIONS) for authenticated users
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.is_authenticated
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

        # Check if this is a list/create action (no pk in URL)
        # For list actions, we allow access and filter in queryset or check in has_object_permission
        lookup_url_kwarg = getattr(view, 'lookup_url_kwarg', None) or 'pk'
        has_lookup_param = lookup_url_kwarg in view.kwargs
        
        # If no lookup parameter, it's a list/create action - allow access
        if not has_lookup_param:
            return True
        
        # For detail actions (has pk), try to get the object and check website
        # But only if get_object() can be safely called
        if hasattr(view, 'get_object') and has_lookup_param:
            try:
                obj = view.get_object()
                return getattr(obj, 'website', None) == website
            except (AssertionError, AttributeError, KeyError):
                # If get_object() fails for any reason, allow access
                # Object-level permission will be checked in has_object_permission
                pass

        # Default to allowing access - object-level checks will happen in has_object_permission
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.
        """
        if not request.user.is_authenticated or not request.user.is_staff:
            return False
        
        website = getattr(request.user, 'website', None)
        if not website:
            return False
        
        # Check if object belongs to the same website
        obj_website = getattr(obj, 'website', None)
        return obj_website == website