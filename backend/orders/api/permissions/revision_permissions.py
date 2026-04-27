from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class BaseRevisionTenantPermission(BasePlatformPermission):
    """
    Base permission enforcing resolved tenant alignment.
    """

    message = "Cross-tenant access denied."
    require_tenant = True

    def _same_tenant(self, request: Request, obj: Any) -> bool:
        website = getattr(request, "website", None)
        obj_website_id = getattr(obj, "website_id", None)

        return obj_website_id == getattr(website, "id", None)


class CanRequestRevision(BaseRevisionTenantPermission):
    """
    Client owner or permitted internal user can request revision.
    """

    message = "You are not allowed to request revision for this order."
    required_permission = "orders.request_revision"

    def has_object_permission(# type: ignore[override] 
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
            permission_code="orders.manage_revisions",
            website=website,
        ):
            return True

        client = getattr(obj, "client", None)
        return getattr(client, "pk", None) == getattr(user, "pk", None)