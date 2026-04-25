from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class CanViewOrderLifecycle(BasePermission):
    """
    Allow lifecycle access to client owner, current assigned writer,
    or same-tenant staff.
    """

    message = "You are not allowed to view this order lifecycle."

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> Any:
        user = request.user

        order_website = getattr(obj, "website", None)
        order_website_id = getattr(order_website, "pk", None)
        user_website_id = getattr(user, "website_id", None)

        if order_website_id != user_website_id:
            return False

        if getattr(user, "is_staff", False):
            return True

        client = getattr(obj, "client", None)
        client_id = getattr(client, "pk", None)
        user_id = getattr(user, "pk", None)

        if client_id == user_id:
            return True

        assignments = getattr(obj, "assignments", None)
        if assignments is None:
            return False

        return assignments.filter(
            writer=user,
            is_current=True,
        ).exists()