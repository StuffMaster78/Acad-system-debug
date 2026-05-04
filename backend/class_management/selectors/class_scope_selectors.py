from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import ClassScopeItem, ClassTask


class ClassScopeSelector:
    """
    Read/query helpers for scope items and tasks.
    """

    @staticmethod
    def scope_items_for_order(*, class_order) -> QuerySet[ClassScopeItem]:
        return ClassScopeItem.objects.filter(
            class_order=class_order,
        ).order_by("due_at", "created_at")

    @staticmethod
    def tasks_for_order(*, class_order) -> QuerySet[ClassTask]:
        return (
            ClassTask.objects.filter(class_order=class_order)
            .select_related("assigned_writer", "scope_item")
            .order_by("due_at", "created_at")
        )

    @staticmethod
    def tasks_for_writer(*, website, writer) -> QuerySet[ClassTask]:
        return (
            ClassTask.objects.filter(
                class_order__website=website,
                assigned_writer=writer,
            )
            .select_related("class_order", "scope_item")
            .order_by("due_at", "created_at")
        )

    @staticmethod
    def due_tasks_for_writer(*, website, writer) -> QuerySet[ClassTask]:
        return ClassScopeSelector.tasks_for_writer(
            website=website,
            writer=writer,
        ).exclude(
            status__in=["completed", "cancelled"],
        )