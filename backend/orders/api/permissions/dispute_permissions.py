from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class BaseDisputeTenantPermission(BasePlatformPermission):
    """
    Base permission enforcing resolved tenant alignment.
    """

    message = "Cross-tenant access denied."
    require_tenant = True

    def _same_tenant(self, request: Request, obj: Any) -> bool:
        website = getattr(request, "website", None)
        return getattr(obj, "website_id", None) == getattr(website, "id", None)


class CanOpenDispute(BaseDisputeTenantPermission):
    """
    Client owner, current writer, or permitted internal user can open a dispute.
    """

    message = "You are not allowed to open a dispute for this order."
    required_permission = "orders.open_dispute"

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
            permission_code="orders.manage_disputes",
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


class CanEscalateDispute(BaseDisputeTenantPermission):
    """
    Internal users with dispute escalation permission can escalate disputes.
    """

    message = "You are not allowed to escalate this dispute."
    required_portal = "internal_admin"
    required_permission = "orders.escalate_dispute"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        return self._same_tenant(request, obj)


class CanResolveDispute(BaseDisputeTenantPermission):
    """
    Internal users with dispute resolution permission can resolve disputes.
    """

    message = "You are not allowed to resolve this dispute."
    required_portal = "internal_admin"
    required_permission = "orders.resolve_dispute"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        return self._same_tenant(request, obj)


class CanCloseDispute(BaseDisputeTenantPermission):
    """
    Internal users with dispute close permission can close disputes.
    """

    message = "You are not allowed to close this dispute."
    required_portal = "internal_admin"
    required_permission = "orders.close_dispute"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        return self._same_tenant(request, obj)