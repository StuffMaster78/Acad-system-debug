from __future__ import annotations

from activity.models import ActivityEvent
from activity.realtime.payloads import ActivityRealtimePayloadBuilder


class ActivityRealtimePublisher:
    """
    Publishes activity events to realtime infrastructure.

    This is a placeholder boundary for SSE, Redis pub/sub, or Channels.
    """

    @staticmethod
    def publish(event: ActivityEvent) -> None:
        """
        Publish an activity event to realtime consumers.
        """
        payload = ActivityRealtimePayloadBuilder.build(event)

        try:
            from activity.realtime.channels import publish_activity_payload
        except ImportError:
            return

        publish_activity_payload(payload=payload)