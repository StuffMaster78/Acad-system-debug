from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from users.models.profile import ProfileUpdateRequest
from users.models.user import UserRole


class IsProfileOwner(BasePermission):
    message = "You can only access your own profile resource."

    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        obj_user = getattr(obj, "user", None)
        if obj_user:
            return obj_user.id == user.id

        obj_id = getattr(obj, "id", None)
        return obj_id == user.id


class CanSubmitOwnProfileUpdateRequest(BasePermission):
    message = "You are not allowed to submit a profile update request."

    allowed_roles = {
        UserRole.CLIENT,
        UserRole.WRITER,
    }

    def has_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role in self.allowed_roles
        )


class IsProfileUpdateOwner(BasePermission):
    message = "You can only act on your own profile update request."

    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: Request,
        view: APIView,
        obj: ProfileUpdateRequest,
    ) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and obj.user.id == user.id
        )


class CanReviewProfileUpdateRequest(BasePermission):
    message = "You are not allowed to review this profile update request."

    global_roles = {
        UserRole.SUPERADMIN,
    }

    website_staff_roles = {
        UserRole.ADMIN,
        UserRole.EDITOR,
        UserRole.SUPPORT,
    }

    def has_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.role in self.global_roles
                or user.role in self.website_staff_roles
            )
        )

    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: Request,
        view: APIView,
        obj: ProfileUpdateRequest,
    ) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role in self.global_roles:
            return True

        if user.role in self.website_staff_roles:
            if not user.website or not obj.website:
                return False

            return obj.website.id == user.website.id

        return False


class CanCancelOwnProfileUpdateRequest(BasePermission):
    message = "You cannot cancel this profile update request."

    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: Request,
        view: APIView,
        obj: ProfileUpdateRequest,
    ) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and obj.user.id == user.id
        )