from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class BaseReassignmentTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment.
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class CanRequestReassignment(BaseReassignmentTenantPermission):
    """
    Client owner, current writer, or staff can request reassignment.
    """

    message = "You are not allowed to request reassignment."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        if not self._same_tenant(request.user, obj):
            return False

        user = request.user
        user_id = getattr(user, "pk", None)

        if getattr(user, "is_staff", False):
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
    Only staff can review reassignment requests.
    """

    message = "You are not allowed to review this reassignment."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )


class CanCancelReassignment(BaseReassignmentTenantPermission):
    """
    Only the original requester can cancel a reassignment request.
    """

    message = "You are not allowed to cancel this reassignment."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        return (
            self._same_tenant(request.user, obj)
            and getattr(obj, "requested_by", None) == request.user
        )