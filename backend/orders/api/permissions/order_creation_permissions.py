from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission


class CanCreateOrder(BasePermission):
    """
    Control who can create orders.

    Rules:
        1. Authenticated users may create their own orders.
        2. Staff may also create orders on behalf of operational flows.
        3. User must belong to a tenant website.
    """

    message = "You are not allowed to create orders."

    def has_permission(self, request, view) -> Any:
        """
        Return whether the request user may create an order.

        Args:
            request:
                DRF request.
            view:
                DRF view.

        Returns:
            bool:
                True when creation is allowed.
        """
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return False

        website = getattr(user, "website", None)
        if website is None:
            return False

        return True


class CanCreateOrderWithUnpaidAccess(BasePermission):
    """
    Restrict allow_unpaid_access to staff users only.

    This permission is intended to be used inside the view as an
    additional payload-aware guard.
    """

    message = "Only staff can enable unpaid access for order creation."

    def has_permission(self, request, view) -> Any:
        """
        Return whether the request payload is allowed.

        Args:
            request:
                DRF request.
            view:
                DRF view.

        Returns:
            bool:
                True when the unpaid access flag is allowed.
        """
        allow_unpaid_access = bool(
            getattr(request, "data", {}).get("allow_unpaid_access", False)
        )
        if not allow_unpaid_access:
            return True

        user = getattr(request, "user", None)
        return bool(getattr(user, "is_staff", False))