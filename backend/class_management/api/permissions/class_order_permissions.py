from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ClassOrderPermission(BasePermission):
    """
    Permission gate for class orders.

    Admin/staff can manage tenant records.
    Clients can access their own class orders.
    Writers can access assigned class orders.
    """

    def has_object_permission( # type: ignore[override]
            self,
            request,
            view,
            obj,
        ) -> bool:
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_superuser", False):
            return True

        if getattr(user, "is_staff", False):
            return True

        if obj.client_id == user.id:
            return True

        if obj.assigned_writer_id == user.id:
            return request.method in SAFE_METHODS

        return False