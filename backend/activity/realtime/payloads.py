from __future__ import annotations

from typing import Any

from activity.models import ActivityEvent
from activity.renderers.activity_card_renderer import ActivityCardRenderer


class ActivityRealtimePayloadBuilder:
    """
    Builds realtime payloads for activity events.
    """

    @staticmethod
    def build(event: ActivityEvent) -> dict[str, Any]:
        """
        Build a websocket or SSE friendly activity payload.
        """
        return {
            "type": "activity.event",
            "event_id": str(event.id),
            "verb": event.verb,
            "website_id": str(event.website.pk),
            "occurred_at": event.occurred_at.isoformat(),
            "card": ActivityCardRenderer.render(event),
        }