from __future__ import annotations

from typing import Any

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from core.permissions.base import BasePlatformPermission

from accounts.services.permission_service import AccountPermissionService
from accounts.services.portal_access_service import PortalAccessService
from accounts.services.tenant_access_service import TenantAccessService


class CanCreateOrder(BasePlatformPermission):
    """
    Allows clients to create orders on their resolved tenant website.
    """

    message = "You are not allowed to create orders."

    required_portal = "client_portal"
    required_permission = "orders.create"
    require_tenant = True


class CanCreateOrderOnBehalf(BasePlatformPermission):
    """
    Allows internal staff to create orders on behalf of clients.
    """

    message = "You are not allowed to create orders on behalf of clients."

    required_portal = "internal_admin"
    required_permission = "orders.create_on_behalf"
    require_tenant = True


class OrderCreationPayloadGuard:
    """
    Payload-aware guards for order creation.

    Use inside the view after normal permission_classes pass.
    """

    @staticmethod
    def validate_unpaid_access_flag(*, request: Any) -> None:
        allow_unpaid_access = bool(
            getattr(request, "data", {}).get("allow_unpaid_access", False)
        )

        if not allow_unpaid_access:
            return

        user = getattr(request, "user", None)

        if not getattr(user, "is_staff", False):
            raise PermissionDenied(
                "Only staff can enable unpaid access for order creation."
            )
        
class CanAccessOrderCreation(BasePermission):
    message = "You are not allowed to create orders."

    def has_permission(self, request, view):  # type: ignore[override]
        user = request.user
        website = getattr(request, "website", None)

        if not user or not user.is_authenticated:
            return False

        if website is None:
            raise PermissionDenied("Tenant could not be resolved.")

        TenantAccessService.require_access(
            user=user,
            website=website,
        )

        client_flow_allowed = (
            PortalAccessService.user_has_portal_access(
                user=user,
                portal_code="client_portal",
            )
            and AccountPermissionService.user_has_permission(
                user=user,
                permission_code="orders.create",
                website=website,
            )
        )

        staff_flow_allowed = (
            PortalAccessService.user_has_portal_access(
                user=user,
                portal_code="internal_admin",
            )
            and AccountPermissionService.user_has_permission(
                user=user,
                permission_code="orders.create_on_behalf",
                website=website,
            )
        )

        return client_flow_allowed or staff_flow_allowed