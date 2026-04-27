from __future__ import annotations

from typing import Any

from rest_framework.request import Request
from rest_framework.views import APIView

from accounts.services.permission_service import AccountPermissionService
from core.permissions.base import BasePlatformPermission


class CanSubmitDraft(BasePlatformPermission):
    """
    Allow current assigned writer (or permitted internal user) to submit draft.
    """

    message = "You are not allowed to submit this draft."

    required_portal = "writer_portal"
    required_permission = "orders.submit_draft"
    require_tenant = True

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):  
        website = getattr(request, "website", None)

        # Tenant safety
        if getattr(obj, "website_id", None) != getattr(website, "id", None):
            return False

        user = request.user

        # Internal override (admin/support/editor etc)
        if AccountPermissionService.user_has_permission(
            user=user,
            permission_code="orders.review_draft",
            website=website,
        ):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments:
            assignment = assignments.filter(is_current=True).first()
            if assignment:
                return assignment.writer == user

        return getattr(obj, "preferred_writer", None) == user


class CanReviewDraft(BasePlatformPermission):
    """
    Allow internal users to review drafts.
    """

    message = "You are not allowed to review this draft."

    required_portal = "internal_admin"
    required_permission = "orders.review_draft"
    require_tenant = True