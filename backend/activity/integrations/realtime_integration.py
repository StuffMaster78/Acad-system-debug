from __future__ import annotations

from activity.models import ActivityEvent
from activity.realtime.publisher import ActivityRealtimePublisher


class ActivityRealtimeIntegration:
    """
    Bridge for publishing activity events to realtime infrastructure.
    """

    @staticmethod
    def publish_event(*, event: ActivityEvent) -> None:
        """
        Publish an activity event to realtime consumers.
        """
        ActivityRealtimePublisher.publish(event=event)