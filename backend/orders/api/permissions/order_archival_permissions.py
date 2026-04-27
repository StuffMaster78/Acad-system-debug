from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from core.permissions.base import BasePlatformPermission
from orders.models.orders.order import Order


class CanArchiveOrder(BasePlatformPermission):
    """
    Only internal users with archive permission can archive orders.
    """

    message = "You are not allowed to archive this order."

    required_portal = "internal_admin"
    required_permission = "orders.archive_order"
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

        return getattr(obj, "website_id", None) == getattr(website, "id", None)