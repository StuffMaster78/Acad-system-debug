"""
Permissions for the order_pricing_core app.
"""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAuthenticatedAndTenantScoped(BasePermission):
    """
    Require an authenticated user with a website context.
    """

    message = "Authentication and tenant context are required."

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> Any:
        """
        Return whether the request is authenticated and tenant-scoped.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        return hasattr(request, "website") and request.website is not None


class CanManagePricingConfig(BasePermission):
    """
    Require a user who can manage pricing configuration.

    Adapt the role checks to your real account/role implementation.
    """

    message = "You do not have permission to manage pricing settings."

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> Any:
        """
        Return whether the user can manage pricing configuration.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        website = getattr(request, "website", None)
        if website is None:
            return False

        if getattr(user, "is_superuser", False):
            return True

        role = getattr(user, "role", "")
        allowed_roles = {
            "admin",
            "superadmin",
            "editor",
            "pricing_manager",
        }
        return role in allowed_roles


class CanPreviewPricing(BasePermission):
    """
    Require a user who can preview pricing internally.
    """

    message = "You do not have permission to preview pricing."

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> Any:
        """
        Return whether the user can preview pricing.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        website = getattr(request, "website", None)
        if website is None:
            return False

        if getattr(user, "is_superuser", False):
            return True

        role = getattr(user, "role", "")
        allowed_roles = {
            "admin",
            "superadmin",
            "editor",
            "pricing_manager",
            "support",
            "staff",
        }
        return role in allowed_roles