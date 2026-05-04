from __future__ import annotations

from django.db.models import Count, Sum

from class_management.models.class_scope import (
    ClassScopeItem,
    ClassTask,
)
from class_management.models.class_portal_work import (
    ClassPortalWorkLog,
)

class ClassWorkloadMetrics:
    """
    Workload analytics for class orders.
    """

    @staticmethod
    def item_type_breakdown(*, website):
        return (
            ClassScopeItem.objects.filter(class_order__website=website)
            .values("item_type")
            .annotate(
                count=Count("id"),
                total_quantity=Sum("quantity"),
                estimated_hours=Sum("estimated_hours"),
            )
            .order_by("-total_quantity")
        )

    @staticmethod
    def task_status_breakdown(*, website):
        return (
            ClassTask.objects.filter(class_order__website=website)
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
    
    @staticmethod
    def portal_activity_breakdown(*, website):
        return (
            ClassPortalWorkLog.objects.filter(class_order__website=website)
            .values("activity_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )