from __future__ import annotations

from django.db.models import QuerySet

from activity.models import ActivityEvent
from activity.selectors.event_selectors import ActivityEventSelector


class ActivityTimelineSelector:
    """
    Read helpers for object timelines.
    """

    @staticmethod
    def for_object(
        *,
        website,
        target,
        user,
    ) -> QuerySet[ActivityEvent]:
        """
        Return visible timeline events for a target object.
        """
        base_queryset = ActivityEventSelector.for_target(
            website=website,
            target=target,
        )
        audience = ActivityEventSelector.get_user_audience(user=user)

        return base_queryset.filter(
            audiences__contains=[audience],
        ).select_related(
            "website",
            "actor_content_type",
            "target_content_type",
            "subject_content_type",
        )