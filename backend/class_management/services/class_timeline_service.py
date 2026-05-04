from __future__ import annotations

from typing import Any

from class_management.models import ClassOrder, ClassTimelineEvent


class ClassTimelineService:
    """
    Service for writing immutable class timeline events.
    """

    @staticmethod
    def record(
        *,
        class_order: ClassOrder,
        event_type: str,
        title: str,
        description: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> ClassTimelineEvent:
        """
        Create a timeline event for a class order.
        """
        return ClassTimelineEvent.objects.create(
            class_order=class_order,
            event_type=event_type,
            title=title,
            description=description,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )