from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class CanSubmitOrderForQA(BasePlatformPermission):
    """
    Allow assigned writer or internal staff to submit an order for QA.
    """

    message = "You are not allowed to submit this order for QA."

    required_permission = "orders.submit_for_qa"
    require_tenant = True

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool: 
        user = getattr(request, "user", None)
        website = getattr(request, "website", None)

        if user is None or not getattr(user, "is_authenticated", False):
            return False

        if getattr(obj, "website_id", None) != getattr(website, "id", None):
            return False

        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.submit_for_qa",
            website=website,
        ):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is not None:
            current_assignment = assignments.filter(is_current=True).first()
            if current_assignment is not None:
                return current_assignment.writer == user

        return getattr(obj, "preferred_writer", None) == user


class CanReviewOrderQA(BasePlatformPermission):
    """
    Allow internal QA/editor/staff users to approve or return QA submissions.
    """

    message = "You are not allowed to review this order for QA."

    required_portal = "internal_admin"
    required_permission = "quality.approve_delivery"
    require_tenant = True

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        website = getattr(request, "website", None)

        return getattr(obj, "website_id", None) == getattr(website, "id", None)