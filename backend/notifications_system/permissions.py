"""
Notification-specific DRF permissions.
"""
from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsNotificationOwner(BasePermission):
    """
    Allows access only to the owner of a notification.
    Used on NotificationFeedViewSet to prevent users
    reading each other's notifications.
    """

    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore[override]
        return obj.user == request.user


class IsWebsiteScoped(BasePermission):
    """
    Ensures the object belongs to the requesting user's website.
    Prevents cross-tenant data access.
    """

    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore[override]
        user_website = getattr(request.user, 'website', None)
        obj_website = getattr(obj, 'website', None)
        if not user_website or not obj_website:
            return False
        return obj_website == user_website