from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class BaseDisputeTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment.
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class CanOpenDispute(BaseDisputeTenantPermission):
    """
    Client owner, current writer, or staff can open a dispute.
    """

    message = "You are not allowed to open a dispute for this order."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
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


class CanEscalateDispute(BaseDisputeTenantPermission):
    """
    Only same-tenant staff can escalate disputes.
    """

    message = "You are not allowed to escalate this dispute."

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


class CanResolveDispute(BaseDisputeTenantPermission):
    """
    Only same-tenant staff can resolve disputes.
    """

    message = "You are not allowed to resolve this dispute."

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


class CanCloseDispute(BaseDisputeTenantPermission):
    """
    Only same-tenant staff can close disputes.
    """

    message = "You are not allowed to close this dispute."

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