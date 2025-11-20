# notifications/tasks/backfill_profiles.py
from celery import shared_task # type: ignore
from django.contrib.auth import get_user_model
from notifications_system.enums import NotificationType, NotificationPriority



User = get_user_model()

@shared_task(bind=True, max_retries=3)
def handle_event(self, event_key, payload):
    """
    Handle an event by sending a notification to the user based on their role.
    """
    from notifications_system.services.core import NotificationService
    try:
        user_id = payload.get("user_id")
        user = User.objects.get(id=user_id)
        website = payload.get("website")

        # You can map event_key to NotificationType here if needed
        notification_type = NotificationType[event_key.upper()]

        NotificationService.send_notification(
            user=user,
            notification_type=notification_type,
            subject=payload.get("subject", "Notification"),
            message=payload.get("message", ""),
            priority=payload.get("priority", NotificationPriority.NORMAL),
            payload=payload,
            website=website,
        )
    except Exception as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
