from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ClassScopePermission(BasePermission):
    """
    Permission for class scope and tasks.
    """

    def has_object_permission( # type: ignore[override]
            self,
            request,
            view,
            obj
        ) -> bool:
        user = request.user

        if not user or not user.is_authenticated:
            return False

        class_order = getattr(obj, "class_order", obj)

        if getattr(user, "is_superuser", False):
            return True

        if getattr(user, "is_staff", False):
            return True

        if class_order.client_id == user.id:
            return request.method in SAFE_METHODS

        if class_order.assigned_writer_id == user.id:
            return request.method in SAFE_METHODS

        return False