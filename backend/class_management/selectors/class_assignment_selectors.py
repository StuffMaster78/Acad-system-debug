from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import ClassAssignment


class ClassAssignmentSelector:
    """
    Read/query helpers for class assignments.
    """

    @staticmethod
    def assignments_for_order(*, class_order) -> QuerySet[ClassAssignment]:
        return (
            ClassAssignment.objects.filter(class_order=class_order)
            .select_related("writer", "assigned_by")
            .order_by("-assigned_at")
        )

    @staticmethod
    def active_assignment(*, class_order) -> ClassAssignment | None:
        return (
            ClassAssignment.objects.filter(
                class_order=class_order,
                status="active",
            )
            .select_related("writer")
            .first()
        )

    @staticmethod
    def assignments_for_writer(*, website, writer):
        return (
            ClassAssignment.objects.filter(
                class_order__website=website,
                writer=writer,
            )
            .select_related("class_order", "assigned_by")
            .order_by("-assigned_at")
        )