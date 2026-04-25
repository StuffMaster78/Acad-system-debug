from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from orders.models.orders.order import Order


class CanCancelOrder(BasePermission):
    """
    Permission for cancelling orders.

    Rules (current simplified version):
        1. User must be authenticated.
        2. User must belong to the same tenant (website).
        3. User must be either:
            - the client who owns the order, OR
            - staff (support/admin/editor/superadmin)

    NOTE:
        Tighten role checks later when your roles system is finalized.
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

        # Client can cancel their own order
        if getattr(obj, "client_user", None) == user:
            return True

        # Staff can cancel
        return bool(getattr(user, "is_staff", False))