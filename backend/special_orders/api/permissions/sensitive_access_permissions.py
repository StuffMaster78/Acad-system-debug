from __future__ import annotations

from typing import Any
from rest_framework.permissions import BasePermission


class SpecialOrderSensitiveAccessPermission(BasePermission):
    """
    Role permission for sensitive special order access.
    """

    ADMIN_ROLES = {
        "admin",
        "superadmin",
    }

    STAFF_ROLES = {
        "admin",
        "superadmin",
        "support",
        "editor",
        "content_manager",
    }

    message = "You do not have permission to access sensitive details."

    @staticmethod
    def _role(user) -> str:
        return str(getattr(user, "role", "")).lower()

    @classmethod
    def is_admin(cls, user) -> bool:
        return cls._role(user) in cls.ADMIN_ROLES

    @classmethod
    def is_staff_user(cls, user) -> bool:
        return cls._role(user) in cls.STAFF_ROLES

    @staticmethod
    def same_website(user, obj) -> bool:
        return (
            getattr(user, "website_id", None)
            == getattr(obj, "website_id", None)
        )


class CanManageSensitiveAccess(SpecialOrderSensitiveAccessPermission):
    """
    Admins and superadmins can create vaults, grants, and revocations.
    """

    def has_object_permission( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            request: Any,
            view: Any,
            obj: Any
        ) -> bool:
        if not self.same_website(request.user, obj):
            return False

        return self.is_admin(request.user)


class CanCreateOwnSensitiveAccess(SpecialOrderSensitiveAccessPermission):
    """
    Clients and admins can submit sensitive access details.
    """

    def has_permission( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            request: Any,
            view: Any,
        ) -> bool:
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return self._role(user) in {
            "client",
            "admin",
            "superadmin",
        }


class CanRevealSensitiveAccess(SpecialOrderSensitiveAccessPermission):
    """
    Admins can reveal by default.

    Non-admin access is checked by the sensitive access service because
    grants can expire and have different access levels.
    """

    def has_object_permission( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            request: Any,
            view: Any,
            obj: Any,
        ) -> bool:
        if not self.same_website(request.user, obj):
            return False

        return True


class CanViewSensitiveAccessLogs(SpecialOrderSensitiveAccessPermission):
    """
    Admins can view sensitive access logs.
    """

    def has_object_permission( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            request: Any,
            view: Any,
            obj: Any,
        ) -> bool:
        if not self.same_website(request.user, obj):
            return False

        return self.is_admin(request.user)


class CanManageTwoFactorRequest(SpecialOrderSensitiveAccessPermission):
    """
    Staff can request 2FA if they have access through the service.
    """

    def has_object_permission( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            request: Any,
            view: Any,
            obj: Any,
    )-> bool:
        if not self.same_website(request.user, obj):
            return False

        return self.is_staff_user(request.user)