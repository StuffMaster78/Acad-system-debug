# notifications/tasks/email_fallback.py
from celery import shared_task
from django.utils.timezone import now, timedelta
from notifications_system.models.notifications import Notification
from notifications_system.services.delivery import NotificationDeliveryService

@shared_task
def send_email_fallbacks():
    threshold = now() - timedelta(hours=3)
    unsent_notifications = Notification.objects.filter(
        is_sent=False,
        channel='web',
        created_at__lte=threshold
    )

    for notification in unsent_notifications:
        NotificationDeliveryService.deliver_via_email(notification)
        notification.is_sent = True
        notification.save()