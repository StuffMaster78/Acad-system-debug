from celery import shared_task # type: ignore
from notifications_system.services.core import NotificationService
from notifications_system.notification_enums import NotificationType
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def async_send_notification(
    self,
    user_id,
    event,
    context=None,
    website_id=None,
    actor_id=None,
    channels=None,
    category="info",
    priority=5,
    template_name=None,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False
):
    """A Celery task to send a notification to the user asynchronously."""
    try:
        from django.contrib.auth import get_user_model
        from websites.models import Website

        User = get_user_model()
        user = User.objects.get(id=user_id)
        website = Website.objects.get(id=website_id) if website_id else None
        actor = User.objects.get(id=actor_id) if actor_id else None

        return NotificationService.send(
            user=user,
            event=event,
            context=context or {},
            website=website,
            actor=actor,
            channels=channels or [NotificationType.IN_APP],
            category=category,
            priority=priority,
            template_name=template_name,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent
        )

    except Exception as e:
        logger.error(
            f"[async_send_notification] Failed for user {user_id}: {e}",
            exc_info=True
        )
        self.retry(exc=e, countdown=60)