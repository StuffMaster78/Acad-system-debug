from __future__ import annotations

from rest_framework.permissions import BasePermission


class ClassAccessPermission(BasePermission):
    """
    Object-level permission for class access records.
    """

    def has_object_permission(  # type: ignore[override]
        self,
        request,
        view,
        obj,
    ) -> bool:
        """
        Allow staff, class client, or assigned writer.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_staff", False):
            return True

        if getattr(user, "is_superuser", False):
            return True

        if getattr(obj, "client_id", None) == getattr(user, "pk", None):
            return True

        if getattr(obj, "assigned_writer_id", None) == getattr(
            user,
            "pk",
            None,
        ):
            return True

        return False