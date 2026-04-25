from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

class CanViewOrderOpsDashboard(BasePermission):
    """
    Restrict operations dashboard visibility to staff users.
    """

    message = "You are not allowed to view the order operations dashboard."

    def has_permission(self, request: Request, view: APIView) -> Any:
        """
        Return whether the request user may view order ops dashboard.
        """
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return False

        if not getattr(user, "is_staff", False):
            return False

        website = getattr(user, "website", None)
        if website is None:
            return False

        return True