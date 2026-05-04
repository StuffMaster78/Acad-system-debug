from __future__ import annotations

from django.db.models import Count, Sum

from class_management.models.class_assignment import (
    ClassAssignment,
)
from class_management.models.class_scope import (
    ClassTask,
)
from class_management.models.class_writer_compensation import (
    ClassWriterCompensation,
)


class ClassWriterMetrics:
    """
    Writer performance and payout metrics.
    """

    @staticmethod
    def writer_assignment_summary(*, website):
        return (
            ClassAssignment.objects.filter(class_order__website=website)
            .values("writer_id", "writer__email")
            .annotate(
                assignments=Count("id"),
            )
            .order_by("-assignments")
        )

    @staticmethod
    def writer_task_summary(*, website):
        return (
            ClassTask.objects.filter(class_order__website=website)
            .values("assigned_writer_id", "assigned_writer__email")
            .annotate(
                tasks=Count("id"),
            )
            .order_by("-tasks")
        )

    @staticmethod
    def writer_compensation_summary(*, website):
        return (
            ClassWriterCompensation.objects.filter(
                class_order__website=website,
            )
            .values("writer_id", "writer__email")
            .annotate(
                total_earned=Sum("final_amount"),
                total_paid=Sum("paid_amount"),
                records=Count("id"),
            )
            .order_by("-total_earned")
        )