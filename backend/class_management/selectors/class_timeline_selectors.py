from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import ClassTimelineEvent


class ClassTimelineSelector:
    """
    Read/query helpers for class timeline events.
    """

    @staticmethod
    def for_order(*, class_order) -> QuerySet[ClassTimelineEvent]:
        return (
            ClassTimelineEvent.objects.filter(class_order=class_order)
            .select_related("triggered_by")
            .order_by("-created_at")
        )