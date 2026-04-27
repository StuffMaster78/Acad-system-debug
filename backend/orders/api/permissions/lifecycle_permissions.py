from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class CanViewOrderLifecycle(BasePlatformPermission):
    """
    Allow lifecycle access to:
        1. permitted internal users
        2. client owner
        3. current assigned writer
    """

    message = "You are not allowed to view this order lifecycle."

    required_permission = "orders.view_lifecycle"
    require_tenant = True

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        user = request.user
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