from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from orders.models.orders.order import Order


class CanArchiveOrder(BasePermission):
    """
    Permission for archiving orders.

    Rules:
        1. User must be authenticated.
        2. Same tenant enforcement.
        3. Only staff can archive orders.

    Rationale:
        Archival is an operational/administrative action,
        not a client-facing one.
    """

    def has_permission(self, request: Request, view: APIView) -> Any:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        if not isinstance(obj, Order):
            return False

        user = request.user

        # Tenant enforcement
        if getattr(user, "website_id", None) != obj.website.pk:
            return False

        # Only staff can archive
        return bool(getattr(user, "is_staff", False))