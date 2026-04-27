from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class BaseAdjustmentTenantPermission(BasePlatformPermission):
    """
    Base permission enforcing resolved tenant alignment.
    """

    message = "Cross-tenant access denied."
    require_tenant = True

    def _same_tenant(self, request: Request, obj: Any) -> bool:
        website = getattr(request, "website", None)

        order = getattr(obj, "order", None)
        target = order if order is not None else obj

        return getattr(target, "website_id", None) == getattr(website, "id", None)


class CanActOnOwnAdjustment(BaseAdjustmentTenantPermission):
    """
    Allow clients to act only on their own order adjustments.
    """

    message = "You are not allowed to act on this adjustment."
    required_permission = "orders.adjust_own"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):  
        if not self._same_tenant(request, obj):
            return False

        order = getattr(obj, "order", None)
        return getattr(order, "client", None) == request.user


class CanWriterEscalateAdjustment(BaseAdjustmentTenantPermission):
    """
    Allow the current assigned writer to escalate an adjustment.
    """

    message = "You are not allowed to escalate this adjustment."
    required_portal = "writer_portal"
    required_permission = "orders.escalate_adjustment"

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        if not self._same_tenant(request, obj):
            return False

        order = getattr(obj, "order", None)
        assignments = getattr(order, "assignments", None)

        if assignments is not None:
            assignment = assignments.filter(is_current=True).first()
            if assignment is not None:
                return assignment.writer == request.user

        return getattr(order, "preferred_writer", None) == request.user


class CanStaffResolveAdjustment(BaseAdjustmentTenantPermission):
    """
    Allow internal users to resolve adjustment escalations.
    """

    message = "You are not allowed to resolve this adjustment."
    required_portal = "internal_admin"
    required_permission = "orders.resolve_adjustment"


class CanCreateAdjustment(BaseAdjustmentTenantPermission):
    """
    Allow current assigned writer or permitted internal user to create adjustment.
    """

    message = "You are not allowed to create this adjustment request."
    required_permission = "orders.create_adjustment"

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
            permission_code="orders.manage_adjustments",
            website=website,
        ):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        return assignments.filter(
            writer=user,
            is_current=True,
        ).exists()


class BaseClientOrStaffAdjustmentPermission(BaseAdjustmentTenantPermission):
    """
    Base class for adjustment actions allowed to client owner
    or permitted internal users.
    """

    required_permission = "orders.respond_adjustment"

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
            permission_code="orders.manage_adjustments",
            website=website,
        ):
            return True

        order = getattr(obj, "order", None)
        client = getattr(order, "client", None)

        return getattr(client, "pk", None) == getattr(user, "pk", None)


class CanCounterAdjustment(BaseClientOrStaffAdjustmentPermission):
    """
    Client owner or permitted internal user can counter an adjustment.
    """

    message = "You are not allowed to counter this adjustment."


class CanAcceptAdjustment(BaseClientOrStaffAdjustmentPermission):
    """
    Client owner or permitted internal user can accept an adjustment.
    """

    message = "You are not allowed to accept this adjustment."


class CanDeclineAdjustment(BaseClientOrStaffAdjustmentPermission):
    """
    Client owner or permitted internal user can decline an adjustment.
    """

    message = "You are not allowed to decline this adjustment."


class CanCancelAdjustment(BaseAdjustmentTenantPermission):
    """
    Original requester or permitted internal user can cancel adjustment.
    """

    message = "You are not allowed to cancel this adjustment."
    required_permission = "orders.cancel_adjustment"

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
            permission_code="orders.manage_adjustments",
            website=website,
        ):
            return True

        return getattr(obj, "requested_by", None) == user


class CanOverrideAdjustment(BaseAdjustmentTenantPermission):
    """
    Allow internal users to create override proposals.
    """

    message = "You are not allowed to override this adjustment."
    required_portal = "internal_admin"
    required_permission = "orders.override_adjustment"