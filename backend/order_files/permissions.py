from rest_framework import permissions

class IsAdminOrSupport(permissions.BasePermission):
    """Allows Admins & Support to manage files and approve requests."""
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.groups.filter(name="Support").exists()

class IsEditorOrSupport(permissions.BasePermission):
    """Allows Editors, Admins, and Support to manage Final Drafts."""
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.groups.filter(name__in=["Editor", "Support"]).exists()

class CanDownloadFile(permissions.BasePermission):
    """Allows only authorized users to download files."""
    def has_object_permission(self, request, view, obj):
        return obj.check_download_access(request.user)

class CanUploadFile(permissions.BasePermission):
    """Only Writers, Editors, Support, and Admins can upload files."""
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.groups.filter(name__in=["Writer", "Editor", "Support"]).exists()