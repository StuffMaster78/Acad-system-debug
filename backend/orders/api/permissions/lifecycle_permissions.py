from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class CanViewOrderLifecycle(BasePlatformPermission):
    """
    Allow lifecycle access to:
        1. permitted internal users (orders.view_lifecycle)
        2. client owner  (checked in has_object_permission)
        3. current assigned writer  (checked in has_object_permission)
    """

    message = "You are not allowed to view this order lifecycle."

    # No required_permission at the view level — ownership / staff permission
    # is verified per-object so we only gate on authentication here.
    required_permission = None
    require_tenant = False

    def has_permission(self, request: Request, view: APIView) -> bool:  # type: ignore[override]
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        user = request.user
        if user.is_superuser or getattr(user, "role", None) == "superadmin":
            return True
        website = getattr(request, "website", None)

        if getattr(obj, "website_id", None) != getattr(website, "id", None):
            return False

        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.view_all_lifecycle",
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