from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class BaseReassignmentTenantPermission(BasePlatformPermission):
    """
    Base permission enforcing resolved tenant alignment.
    """

    message = "Cross-tenant access denied."
    require_tenant = True

    def _same_tenant(self, request: Request, obj: Any) -> bool:
        website = getattr(request, "website", None)
        obj_website_id = getattr(obj, "website_id", None)

        return obj_website_id == getattr(website, "id", None)


class CanRequestReassignment(BaseReassignmentTenantPermission):
    """
    Client owner, current writer, or permitted internal user can request reassignment.
    """

    message = "You are not allowed to request reassignment."
    required_permission = "orders.request_reassignment"

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
        user_id = getattr(user, "pk", None)

        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.review_reassignment",
            website=website,
        ):
            return True

        client = getattr(obj, "client", None)
        if getattr(client, "pk", None) == user_id:
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        return assignments.filter(
            writer=user,
            is_current=True,
        ).exists()


class CanReviewReassignment(BaseReassignmentTenantPermission):
    """
    Internal users with reassignment review permission can review requests.
    """

    message = "You are not allowed to review this reassignment."
    required_portal = "internal_admin"
    required_permission = "orders.review_reassignment"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):  
        return self._same_tenant(request, obj)


class CanCancelReassignment(BaseReassignmentTenantPermission):
    """
    Original requester or permitted internal user can cancel a reassignment request.
    """

    message = "You are not allowed to cancel this reassignment."
    required_permission = "orders.cancel_reassignment"

    def has_object_permission( # type: ignore
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):  # type: ignore[override]
        if not self._same_tenant(request, obj):
            return False

        user = request.user
        website = getattr(request, "website", None)

        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.review_reassignment",
            website=website,
        ):
            return True

        return getattr(obj, "requested_by", None) == user