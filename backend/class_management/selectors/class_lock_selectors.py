from __future__ import annotations

from class_management.models import ClassOrder


class ClassLockSelector:
    """
    Row-level locks for dangerous class operations.
    """

    @staticmethod
    def lock_order(*, class_order_id: int) -> ClassOrder:
        return ClassOrder.objects.select_for_update().get(pk=class_order_id)