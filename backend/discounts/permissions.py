from __future__ import annotations

from rest_framework import permissions


DISCOUNT_MANAGEMENT_ROLES = {
    "admin",
    "superadmin",
}

DISCOUNT_SUPPORT_ROLES = {
    "support",
}

CLIENT_ROLE = "client"


def get_user_role(user) -> str | None:
    """
    Return the user's platform role.
    """
    return getattr(user, "role", None)


class CanUseClientDiscounts(permissions.BasePermission):
    """
    Allow clients to preview and apply website scoped discounts.
    """

    def has_permission(self, request, view) -> bool:
        """
        Return whether the user can use client discounts.
        """
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "website_id", None)
            and get_user_role(user) == CLIENT_ROLE
        )


class CanViewDiscounts(permissions.BasePermission):
    """
    Allow discount visibility for support and managers.
    """

    def has_permission(self, request, view) -> bool:
        """
        Return whether the user can view discount records.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return get_user_role(user) in (
            DISCOUNT_MANAGEMENT_ROLES | DISCOUNT_SUPPORT_ROLES
        )


class CanManageDiscounts(permissions.BasePermission):
    """
    Allow discount creation and mutation.
    """

    def has_permission(self, request, view) -> bool:
        """
        Return whether the user can manage discounts.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return get_user_role(user) in DISCOUNT_MANAGEMENT_ROLES


class CanViewDiscountDashboard(permissions.BasePermission):
    """
    Allow dashboard visibility for support and managers.
    """

    def has_permission(self, request, view) -> bool:
        """
        Return whether the user can view dashboard data.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return get_user_role(user) in (
            DISCOUNT_MANAGEMENT_ROLES | DISCOUNT_SUPPORT_ROLES
        )