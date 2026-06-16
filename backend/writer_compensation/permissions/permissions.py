from __future__ import annotations

from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAdminUser(BasePermission):
    """Site admin — full access to all compensation data and actions."""

    def has_permission(self, request, view) -> bool: #type: ignore
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )


class IsWriter(BasePermission):
    """
    Authenticated writer — read own data only.
    Views must additionally filter by request.user.writer_profile.
    Uses get_writer_profile() because WriterProfile links through
    AccountProfile, not directly to User.
    """

    def has_permission(self, request, view) -> bool: #type: ignore
        if not (request.user and request.user.is_authenticated):
            return False
        from writer_management.utils import get_writer_profile
        return get_writer_profile(request.user) is not None


class IsSupport(BasePermission):
    """
    Support staff — read-only access to all writer data.
    Can flag and escalate but cannot mutate compensation records.
    """

    def has_permission(self, request, view) -> bool: #type: ignore
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_support", False)
        )


class IsAdminOrSupport(BasePermission):
    """Admin or support — used on read endpoints accessible to both."""

    def has_permission(self, request, view) -> bool: #type: ignore
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return (
            user.is_staff
            or user.is_superuser
            or getattr(user, "is_support", False)
        )

class CanManageRewards(
    BasePermission,
):
    """
    Allows reward management access.
    """

    def has_permission( #type: ignore
        self,
        request,
        view,
    ):
        return bool(
            request.user
            and request.user.is_staff
        )


class CanViewOwnRewards(
    BasePermission,
):
    """
    Writers may only view their own rewards.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return (
            obj.writer.user_id
            == request.user.id
        )


class CanRunRewardJobs(
    BasePermission,
):
    """
    Restrict scheduler endpoints.
    """

    def has_permission( #type: ignore
        self,
        request,
        view,
    ):
        return bool(
            request.user
            and request.user.is_superuser
        )