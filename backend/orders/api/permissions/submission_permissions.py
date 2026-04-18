from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission


class BaseSubmissionTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment.
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class CanSubmitOrder(BaseSubmissionTenantPermission):
    """
    Only the current assigned writer can submit the order.
    """

    message = "You are not allowed to submit this order."

    def has_object_permission(self, request, view, obj) -> bool:
        if not self._same_tenant(request.user, obj):
            return False

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        return assignments.filter(
            writer=request.user,
            is_current=True,
        ).exists()


class CanCompleteOrder(BaseSubmissionTenantPermission):
    """
    Client owner or same-tenant staff can complete the order.
    """

    message = "You are not allowed to complete this order."

    def has_object_permission(self, request, view, obj) -> bool:
        if not self._same_tenant(request.user, obj):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        client = getattr(obj, "client", None)
        return getattr(client, "pk", None) == getattr(
            request.user,
            "pk",
            None,
        )


class CanReopenOrder(BaseSubmissionTenantPermission):
    """
    Only same-tenant staff can reopen completed orders.
    """

    message = "You are not allowed to reopen this order."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )