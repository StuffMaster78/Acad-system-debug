from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class BaseApprovalTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment for approval actions.
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        """
        Return whether the user and object belong to the same tenant.

        Args:
            user:
                Request user.
            obj:
                Target object.

        Returns:
            bool:
                True when both belong to the same tenant.
        """
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class CanApproveOrder(BaseApprovalTenantPermission):
    """
    Allow explicit approval by the client owner or same-tenant staff.
    """

    message = "You are not allowed to approve this order."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        """
        Return whether the actor may approve the order.

        Args:
            request:
                DRF request.
            view:
                DRF view.
            obj:
                Target order.

        Returns:
            bool:
                True when approval is allowed.
        """
        if not self._same_tenant(request.user, obj):
            return False

        if getattr(request.user, "is_staff", False):
            return True

        client = getattr(obj, "client", None)
        client_id = getattr(client, "pk", None)
        user_id = getattr(request.user, "pk", None)
        return client_id == user_id