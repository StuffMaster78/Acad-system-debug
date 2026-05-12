from __future__ import annotations

from typing import Any
from typing import Iterable

from activity.models import ActivityEvent
from activity.renderers.activity_card_renderer import ActivityCardRenderer


class ActivityTimelineProjectionService:
    """
    Builds API friendly timeline projections.
    """

    @staticmethod
    def project_event(*, event: ActivityEvent) -> dict[str, Any]:
        """
        Convert one activity event into a timeline card payload.
        """
        return ActivityCardRenderer.render(event)

    @staticmethod
    def project_events(
        *,
        events: Iterable[ActivityEvent],
    ) -> list[dict[str, Any]]:
        """
        Convert activity events into timeline card payloads.
        """
        return [
            ActivityTimelineProjectionService.project_event(event=event)
            for event in events
        ]

    @staticmethod
    def project_grouped_by_day(
        *,
        events: Iterable[ActivityEvent],
    ) -> list[dict[str, Any]]:
        """
        Convert events into day grouped timeline sections.
        """
        grouped_events: dict[str, list[dict[str, Any]]] = {}

        for event in events:
            day_key = event.occurred_at.date().isoformat()
            grouped_events.setdefault(day_key, [])
            grouped_events[day_key].append(
                ActivityTimelineProjectionService.project_event(
                    event=event,
                ),
            )

        return [
            {
                "date": date,
                "events": grouped_events[date],
            }
            for date in grouped_events
        ]