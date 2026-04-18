from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission


class BaseTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment.

    Assumes:
        request.user.website exists
        object.website exists
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class IsStaffUser(BasePermission):
    """
    Allow only staff users.

    Adjust this depending on your role system later.
    """

    message = "Only staff users can perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and getattr(request.user, "is_authenticated", False)
            and getattr(request.user, "is_staff", False)
        )


class IsWriterUser(BasePermission):
    """
    Allow only writer users.

    Adjust based on your role system.
    """

    message = "Only writers can perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and getattr(request.user, "is_authenticated", False)
        )
    
# Action Permissions

class CanRouteOrderToStaffing(BaseTenantPermission):
    """
    Only staff can route an order into staffing.
    """

    message = "You are not allowed to route this order to staffing."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )
    

class CanExpressInterest(BaseTenantPermission):
    """
    Writers can express interest in pool orders.
    """

    message = "You cannot express interest in this order."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and not getattr(request.user, "is_staff", False)
        )
    

class CanWithdrawInterest(BaseTenantPermission):
    """
    Only the owner writer can withdraw interest.
    """

    message = "You cannot withdraw this interest."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(obj, "writer_id", None)
            == getattr(request.user, "pk", None)
        )
    

class CanTakeOrder(BaseTenantPermission):
    """
    Writers can take pool orders.
    """

    message = "You cannot take this order."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and not getattr(request.user, "is_staff", False)
        )


class CanAssignFromInterest(BaseTenantPermission):
    """
    Only staff can assign from interest.
    """

    message = "You cannot assign this interest."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )
    

class CanAssignDirect(BaseTenantPermission):
    """
    Only staff can assign directly.
    """

    message = "You cannot assign this order."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )


class CanAcceptPreferredWriter(BaseTenantPermission):
    """
    Only the invited preferred writer can accept.
    """

    message = "You are not the invited preferred writer."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(obj, "writer_id", None)
            == getattr(request.user, "pk", None)
        )
    

class CanDeclinePreferredWriter(BaseTenantPermission):
    """
    Only the invited preferred writer can decline.
    """

    message = "You are not the invited preferred writer."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(obj, "writer_id", None)
            == getattr(request.user, "pk", None)
        )
    

class CanReleaseToPool(BaseTenantPermission):
    """
    Only staff can release orders back to pool.
    """

    message = "You cannot release this order to pool."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )