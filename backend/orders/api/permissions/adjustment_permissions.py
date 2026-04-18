from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission


class BaseAdjustmentTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment.
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class CanCreateAdjustment(BaseAdjustmentTenantPermission):
    """
    Writers and staff can create adjustment requests for an order.
    """

    message = "You are not allowed to create this adjustment request."

    def has_object_permission(self, request, view, obj) -> bool:
        if not self._same_tenant(request.user, obj):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        return assignments.filter(
            writer=request.user,
            is_current=True,
        ).exists()


class CanCounterAdjustment(BaseAdjustmentTenantPermission):
    """
    Client owner or staff can counter an adjustment request.
    """

    message = "You are not allowed to counter this adjustment."

    def has_object_permission(self, request, view, obj) -> bool:
        if not self._same_tenant(request.user, obj):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        order = getattr(obj, "order", None)
        client = getattr(order, "client", None)
        return getattr(client, "pk", None) == getattr(
            request.user,
            "pk",
            None,
        )


class CanAcceptAdjustment(BaseAdjustmentTenantPermission):
    """
    Client owner or staff can accept an adjustment request.
    """

    message = "You are not allowed to accept this adjustment."

    def has_object_permission(self, request, view, obj) -> bool:
        if not self._same_tenant(request.user, obj):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        order = getattr(obj, "order", None)
        client = getattr(order, "client", None)
        return getattr(client, "pk", None) == getattr(
            request.user,
            "pk",
            None,
        )


class CanDeclineAdjustment(BaseAdjustmentTenantPermission):
    """
    Client owner or staff can decline an adjustment request.
    """

    message = "You are not allowed to decline this adjustment."

    def has_object_permission(self, request, view, obj) -> bool:
        if not self._same_tenant(request.user, obj):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        order = getattr(obj, "order", None)
        client = getattr(order, "client", None)
        return getattr(client, "pk", None) == getattr(
            request.user,
            "pk",
            None,
        )


class CanCancelAdjustment(BaseAdjustmentTenantPermission):
    """
    Requester or staff can cancel an adjustment request.
    """

    message = "You are not allowed to cancel this adjustment."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and (
                getattr(request.user, "is_staff", False)
                or getattr(obj, "requested_by", None) == request.user
            )
        )


class CanOverrideAdjustment(BaseAdjustmentTenantPermission):
    """
    Only staff can create override proposals.
    """

    message = "You are not allowed to override this adjustment."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )