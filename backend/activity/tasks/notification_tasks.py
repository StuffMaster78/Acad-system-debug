from __future__ import annotations

from celery import shared_task

from activity.models import ActivityEvent
from activity.services.activity_notification_orchestrator import (
    ActivityNotificationOrchestrator,
)


@shared_task
def dispatch_activity_notifications(event_id: str) -> None:
    event = ActivityEvent.objects.get(id=event_id)

    ActivityNotificationOrchestrator.handle_event(event=event)