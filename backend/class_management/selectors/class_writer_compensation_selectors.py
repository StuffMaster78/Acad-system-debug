from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import ClassWriterCompensation


class ClassWriterCompensationSelector:
    """
    Read/query helpers for class writer compensation.
    """

    @staticmethod
    def for_order(*, class_order) -> ClassWriterCompensation | None:
        return (
            ClassWriterCompensation.objects.filter(
                class_order=class_order,
            )
            .select_related("writer", "approved_by", "posted_by")
            .first()
        )

    @staticmethod
    def for_writer(*, website, writer) -> QuerySet[ClassWriterCompensation]:
        return (
            ClassWriterCompensation.objects.filter(
                class_order__website=website,
                writer=writer,
            )
            .select_related("class_order")
            .order_by("-created_at")
        )

    @staticmethod
    def earned_unposted(*, website) -> QuerySet[ClassWriterCompensation]:
        return (
            ClassWriterCompensation.objects.filter(
                class_order__website=website,
                status="earned",
            )
            .select_related("class_order", "writer")
            .order_by("earned_at")
        )