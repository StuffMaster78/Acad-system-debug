from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ClassWriterCompensationPermission(BasePermission):
    """
    Permission for writer compensation.

    Staff can manage compensation.
    Writers can read their own compensation.
    Clients cannot see writer compensation.
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

        writer_id = getattr(obj, "writer_id", None)

        if writer_id is None:
            writer_id = getattr(obj, "assigned_writer_id", None)

        if writer_id == user.id:
            return request.method in SAFE_METHODS

        return False