from __future__ import annotations

from activity.models import ActivityEvent


class ActivityNotificationIntegration:
    """
    Optional bridge from activity events to notifications.
    """

    @staticmethod
    def notify_from_event(
        *,
        event: ActivityEvent,
        recipient,
        channels: list[str] | None = None,
    ) -> None:
        """
        Send a notification for an activity event.
        """
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
        except ImportError:
            return

        NotificationService.notify(
            event_key=event.verb,
            recipient=recipient,
            website=event.website,
            context={
                "activity_event_id": str(event.id),
                "title": event.title,
                "summary": event.summary,
                "metadata": event.metadata,
            },
            channels=channels,
            triggered_by=event.actor,
        )