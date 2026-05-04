from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class ClassPaymentPermission(BasePermission):
    """
    Permission for class payment records.
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

        class_order = getattr(obj, "class_order", None)

        if class_order is None and hasattr(obj, "plan"):
            class_order = obj.plan.class_order

        if class_order is None:
            return False

        if getattr(user, "is_superuser", False):
            return True

        if getattr(user, "is_staff", False):
            return True

        if class_order.client_id == user.id:
            return request.method in SAFE_METHODS

        return False