from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class BaseAdjustmentFundingTenantPermission(BasePermission):
    """
    Base permission enforcing tenant alignment.
    """

    message = "Cross-tenant access denied."

    def _same_tenant(self, user: Any, obj: Any) -> bool:
        user_website_id = getattr(user, "website_id", None)

        obj_website = getattr(obj, "website", None)
        obj_website_id = getattr(obj_website, "pk", None)

        return user_website_id == obj_website_id


class CanCreateAdjustmentFunding(BaseAdjustmentFundingTenantPermission):
    """
    Only staff can create adjustment funding records.
    """

    message = "You are not allowed to create adjustment funding."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )


class CanManageAdjustmentFunding(BaseAdjustmentFundingTenantPermission):
    """
    Only staff can manage funding references and apply payments.
    """

    message = "You are not allowed to manage adjustment funding."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        return (
            self._same_tenant(request.user, obj)
            and getattr(request.user, "is_staff", False)
        )