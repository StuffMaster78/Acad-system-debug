from __future__ import annotations
from typing import Any
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from accounts.services.permission_service import AccountPermissionService
from accounts.services.portal_access_service import PortalAccessService
from accounts.services.tenant_access_service import TenantAccessService


class BasePlatformPermission(BasePermission):
    """
    Base permission for enforcing:
        - portal access
        - tenant access
        - action permission
    """

    required_permission: str | None = None
    required_portal: str | None = None
    require_tenant: bool = True

    def has_permission(self, request: Any, view: Any):  # type: ignore[override]
        user = request.user

        if not user or not user.is_authenticated:
            return False
        
        website = getattr(request, "website", None)

        if self.require_tenant and website is None:
            raise PermissionDenied("Tenant could not be resolved.")


        # 1. Portal check
        if self.required_portal:
            PortalAccessService.require_portal_access(
                user=user,
                portal_code=self.required_portal,
            )

        # 2. Tenant check
        if self.require_tenant and request.website:
            TenantAccessService.require_access(
                user=user,
                website=request.website,
            )

        # 3. Permission check
        if self.required_permission:
            AccountPermissionService.require_permission(
                user=user,
                permission_code=self.required_permission,
                website=request.website,
            )

        return True