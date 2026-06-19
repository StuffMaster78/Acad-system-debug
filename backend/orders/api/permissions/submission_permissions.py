from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class BaseSubmissionTenantPermission(BasePlatformPermission):
    """
    Base permission enforcing resolved tenant alignment.
    """

    message = "Cross-tenant access denied."
    require_tenant = True

    def _same_tenant(self, request: Request, obj: Any) -> bool:
        website = getattr(request, "website", None)
        return getattr(obj, "website_id", None) == getattr(website, "id", None)


class CanSubmitOrder(BaseSubmissionTenantPermission):
    """
    Current assigned writer can submit the order.
    """

    message = "You are not allowed to submit this order."

    required_portal = "writer_portal"
    required_permission = "orders.submit_order"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        if not self._same_tenant(request, obj):
            return False

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        # OrderAssignment.writer is a FK to WriterProfile, not User.
        from writer_management.models import WriterProfile
        website = getattr(request, "website", None)
        writer_profile = (
            WriterProfile.objects
            .filter(account_profile__user=request.user, account_profile__website=website)
            .first()
            or WriterProfile.objects.filter(account_profile__user=request.user).first()
        )
        if writer_profile is None:
            return False

        return assignments.filter(
            writer=writer_profile,
            is_current=True,
        ).exists()


class CanCompleteOrder(BaseSubmissionTenantPermission):
    """
    Client owner or permitted internal user can complete the order.
    Authorization is handled entirely in has_object_permission below
    (client-owner check OR staff manage_completion permission).
    required_permission is intentionally omitted so clients are not blocked
    before reaching object-level checks.
    """

    message = "You are not allowed to complete this order."

    required_permission = None

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
            permission_code="orders.manage_completion",
            website=website,
        ):
            return True

        client = getattr(obj, "client", None)
        return getattr(client, "pk", None) == getattr(user, "pk", None)


class CanReopenOrder(BaseSubmissionTenantPermission):
    """
    Internal users with reopen permission can reopen completed orders.
    """

    message = "You are not allowed to reopen this order."

    required_portal = "internal_admin"
    required_permission = "orders.reopen_order"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        return self._same_tenant(request, obj)