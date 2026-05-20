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

    def has_permission(self, request: Request, view: APIView):  # type: ignore[override]
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission( # type: ignore[override]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ):  
        website = _request_website(request=request)

        # Tenant safety
        if _website_id(obj) != _website_id(website):
            return False

        user = request.user

        # Internal override (admin/support/editor etc)
        if _is_staff_like(user=user) or _has_account_permission(
            user=user,
            permission_code="orders.review_draft",
            website=website,
        ):
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments:
            assignment = assignments.filter(is_current=True).first()
            if assignment:
                return _matches_user(candidate=assignment.writer, user=user)

        return _matches_user(
            candidate=getattr(obj, "preferred_writer", None),
            user=user,
        )


class CanReviewDraft(BasePlatformPermission):
    """
    Allow internal users to review drafts.
    """

    message = "You are not allowed to review this draft."

    required_portal = "internal_admin"
    required_permission = "orders.review_draft"
    require_tenant = True

    def has_permission(self, request: Request, view: APIView):  # type: ignore[override]
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if _is_staff_like(user=user):
            return True
        return _has_account_permission(
            user=user,
            permission_code=self.required_permission,
            website=_request_website(request=request),
        )


def _request_website(*, request: Request):
    return getattr(request, "website", None) or getattr(request.user, "website", None)


def _website_id(obj) -> int | None:
    nested_website = getattr(obj, "website", None)
    if nested_website is not None:
        return _website_id(nested_website)
    return getattr(obj, "website_id", None) or getattr(obj, "id", None) or getattr(obj, "pk", None)


def _is_staff_like(*, user) -> bool:
    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or getattr(user, "is_admin", False)
        or getattr(user, "is_super_admin", False)
        or getattr(user, "role", None) in {"admin", "superadmin", "support", "editor"}
    )


def _matches_user(*, candidate, user) -> bool:
    user_id = getattr(user, "id", None) or getattr(user, "pk", None)
    if candidate is None:
        return False
    if getattr(candidate, "id", None) == user_id or getattr(candidate, "pk", None) == user_id:
        return True
    if getattr(candidate, "user_id", None) == user_id:
        return True
    account_profile = getattr(candidate, "account_profile", None)
    return getattr(account_profile, "user_id", None) == user_id


def _has_account_permission(*, user, permission_code: str, website) -> bool:
    try:
        return AccountPermissionService.user_has_permission(
            user=user,
            permission_code=permission_code,
            website=website,
        )
    except Exception:
        return False
