from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class CanViewAchievements(
    BasePermission,
):
    """
    Achievement viewing permission.
    """

    def has_permission( # type: ignore[override]
        self,
        request,
        view,
    ):
        return bool(
            request.user
            and request.user.is_authenticated
        )


class CanManageAchievements(
    BasePermission,
):
    """
    Achievement management permission.
    """

    message = (
        "You cannot manage achievements."
    )

    def has_permission( # type: ignore[override]
        self,
        request,
        view,
    ):
        user = request.user

        if (
            request.method
            in SAFE_METHODS
        ):
            return bool(
                user
                and user.is_authenticated
            )

        return bool(
            user
            and (
                getattr(user, "is_staff", False)
                or getattr(
                    user,
                    "is_superuser",
                    False,
                )
            )
        )