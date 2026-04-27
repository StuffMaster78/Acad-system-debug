from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission
from orders.models.orders.order import Order


class CanCancelOrder(BasePlatformPermission):
    """
    Client owner or permitted internal user can cancel an order.
    """

    message = "You are not allowed to cancel this order."

    required_permission = "orders.cancel_order"
    require_tenant = True

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):
        if not isinstance(obj, Order):
            return False

        website = getattr(request, "website", None)

        if getattr(obj, "website_id", None) != getattr(website, "id", None):
            return False

        user = request.user

        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.cancel_any_order",
            website=website,
        ):
            return True

        client = getattr(obj, "client_user", None) or getattr(obj, "client", None)

        return client == user