"""
writer_management/api/permissions.py

DRF permission classes for the writer_management API.

CLASSES
-------
IsAdminUser          — admin or superadmin role only
IsWriterUser         — has a non-deleted WriterProfile on this website
IsWriterOwner        — is the writer being accessed (object-level)
IsAdminOrWriterOwner — admin OR the owner of the resource
IsAdminOrReadOnly    — read for all authenticated, write for admins only
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS

from writer_management.utils import get_writer_profile_for_website


class IsAdminUser(BasePermission):
    """Admin or superadmin only."""

    message = "Admin access required."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return _has_admin_role(request.user, request)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class IsWriterUser(BasePermission):
    """User must have a non-deleted WriterProfile on this website."""

    message = "Writer access required."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        website = _resolve_website(request)
        if website is None:
            return False
        profile = get_writer_profile_for_website(request.user, website)
        return profile is not None and not profile.is_deleted

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class IsWriterOwner(BasePermission):
    """
    Object-level: requesting user must be the writer being accessed.

    Works when obj is:
        - A WriterProfile (has .registration_id)
        - A related model with a .writer FK to WriterProfile
    """

    message = "You can only access your own writer resources."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        website = _resolve_website(request)
        if website is None:
            return False
        profile = get_writer_profile_for_website(request.user, website)
        if profile is None:
            return False

        # Direct WriterProfile
        if hasattr(obj, "registration_id"):
            return obj.pk == profile.pk

        # Related model (WriterNote, WriterWarning, etc.)
        writer = getattr(obj, "writer", None)
        if writer is not None:
            return writer.pk == profile.pk

        return False


class IsAdminOrWriterOwner(BasePermission):
    """Admin has full access. Writer has access to their own resources."""

    message = "Admin or resource owner access required."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        if _has_admin_role(request.user, request):
            return True

        website = _resolve_website(request)
        if website is None:
            return False
        profile = get_writer_profile_for_website(request.user, website)
        if profile is None:
            return False

        if hasattr(obj, "registration_id"):
            return obj.pk == profile.pk

        writer = getattr(obj, "writer", None)
        return writer is not None and writer.pk == profile.pk


class IsAdminOrReadOnly(BasePermission):
    """Read-only for authenticated users. Write requires admin."""

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _has_admin_role(request.user, request)


# ----------------------------------------------------------------
# PRIVATE HELPERS
# ----------------------------------------------------------------

def _has_admin_role(user, request) -> bool:
    try:
        website = _resolve_website(request)
        if website is None:
            return False
        profile = user.account_profiles.get(website=website)
        return getattr(profile, "role", None) in ("admin", "superadmin")
    except Exception:
        return False


def _resolve_website(request):
    """
    Resolve website from request.
    Expects request.website set by website middleware.
    Falls back through user's account profiles.
    """
    website = getattr(request, "website", None)
    if website is not None:
        return website
    try:
        return request.user.account_profiles.order_by("pk").first().website
    except Exception:
        return None