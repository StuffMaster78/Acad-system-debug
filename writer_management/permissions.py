from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSuperAdmin(BasePermission):
    """
    Allows access only to admins and superadmins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class IsAdminOrSuperAdminOrSupportOrEditor(BasePermission):
    """
    Allows access to admins, superadmins, support staff, and editors.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin', 'support', 'editor']


class IsWriter(BasePermission):
    """
    Allows access only to writers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'writer'


class IsWriterOrAdminOrSuperAdmin(BasePermission):
    """
    Writers can access their own data, while admins and superadmins have full access.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user.role in ['admin', 'superadmin']:
                return True
            if request.user.role == 'writer':
                return obj.writer == request.user.writer_profile  # Ensure writer can only access their own data
        return False


class IsAdminOrSuperAdminOrReadOnly(BasePermission):
    """
    Admins and superadmins have full access, others have read-only access.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class IsSupportOrEditorOrReadOnly(BasePermission):
    """
    Support and editors have full access, others have read-only access.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['support', 'editor']