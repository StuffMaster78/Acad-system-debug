from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission


class BaseHoldTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment.
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class CanRequestHold(BaseHoldTenantPermission):
    """
    Client owner, current writer, or staff can request a hold.
    """

    message = "You are not allowed to request a hold."

    def has_object_permission(self, request, view, obj) -> bool:
        if not self._same_tenant(request.user, obj):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        client = getattr(obj, "client", None)
        if getattr(client, "pk", None) == getattr(request.user, "pk", None):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        return assignments.filter(
            writer=request.user,
            is_current=True,
        ).exists()


class CanReviewHold(BaseHoldTenantPermission):
    """
    Only staff can activate or release a hold.
    """

    message = "You are not allowed to review this hold."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )


class CanCancelHoldRequest(BaseHoldTenantPermission):
    """
    Only the original requester can cancel a pending hold request.
    """

    message = "You are not allowed to cancel this hold request."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(obj, "requested_by", None) == request.user
        )