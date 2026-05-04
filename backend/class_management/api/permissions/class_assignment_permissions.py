from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ClassAssignmentPermission(BasePermission):
    """
    Permission for writer assignment records.
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

        class_order = obj.class_order

        if getattr(user, "is_superuser", False):
            return True

        if getattr(user, "is_staff", False):
            return True

        if obj.writer_id == user.id:
            return request.method in SAFE_METHODS

        if class_order.client_id == user.id:
            return request.method in SAFE_METHODS

        return False