from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class BaseHoldTenantPermission(BasePlatformPermission):
    """
    Base permission enforcing resolved tenant alignment.
    """

    message = "Cross-tenant access denied."
    require_tenant = True

    def _same_tenant(self, request: Request, obj: Any) -> bool:
        website = getattr(request, "website", None)
        return getattr(obj, "website_id", None) == getattr(website, "id", None)


class CanRequestHold(BaseHoldTenantPermission):
    """
    Client owner, current writer, or permitted internal user can request a hold.
    """

    message = "You are not allowed to request a hold."
    required_permission = "orders.request_hold"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        if not self._same_tenant(request, obj):
            return False

        user = request.user
        website = getattr(request, "website", None)

        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.review_hold",
            website=website,
        ):
            return True

        client = getattr(obj, "client", None)
        if getattr(client, "pk", None) == getattr(user, "pk", None):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        return assignments.filter(
            writer=user,
            is_current=True,
        ).exists()


class CanReviewHold(BaseHoldTenantPermission):
    """
    Internal users with hold review permission can activate or release holds.
    """

    message = "You are not allowed to review this hold."
    required_portal = "internal_admin"
    required_permission = "orders.review_hold"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        return self._same_tenant(request, obj)


class CanCancelHoldRequest(BaseHoldTenantPermission):
    """
    Original requester or permitted internal user can cancel a hold request.
    """

    message = "You are not allowed to cancel this hold request."
    required_permission = "orders.cancel_hold"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        if not self._same_tenant(request, obj):
            return False

        user = request.user
        website = getattr(request, "website", None)

        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.review_hold",
            website=website,
        ):
            return True

        return getattr(obj, "requested_by", None) == user