from celery import shared_task # type: ignore
from django.utils.timezone import now, timedelta
from notifications_system.models.notifications import Notification
from notifications_system.services.delivery import NotificationDeliveryService
from notifications_system.utils.fallbacks import FallbackOrchestrator

@shared_task(bind=True, max_retries=3)
def retry_notification_fallback(self, notification_id, tried_channels):
    notification = Notification.objects.get(
        id=notification_id
    )
    orchestrator = FallbackOrchestrator(
        notification, tried_channels=set(tried_channels)
    )

    success = orchestrator.run(async_mode=True)
    if not success:
        # Celery retry with exponential backoff
        delay = orchestrator._retry_delay(
            orchestrator.retry_count
        )
        raise self.retry(countdown=delay)
