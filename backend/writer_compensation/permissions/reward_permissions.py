from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsRewardAdmin(
    BasePermission,
):
    """
    Reward administration permission.
    """

    message = (
        "You do not have permission "
        "to manage reward resources."
    )

    def has_permission( # type: ignore[override]
        self,
        request,
        view,
    ):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return bool(
            getattr(user, "is_superuser", False)
            or getattr(user, "is_staff", False)
        )


class IsRewardViewer(
    BasePermission,
):
    """
    Read-only reward access permission.
    """

    def has_permission( # type: ignore[override]
        self,
        request,
        view,
    ):
        user = request.user

        return bool(
            user
            and user.is_authenticated
        )