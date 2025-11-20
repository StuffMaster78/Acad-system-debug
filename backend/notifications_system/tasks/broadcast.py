from celery import shared_task # type: ignore
from notifications_system.models.broadcast_notification import (
    BroadcastNotification
)
from django.utils.timezone import now, timedelta

@shared_task
def archive_expired_broadcasts():
    """Archive broadcasts that have expired"""
    expired = BroadcastNotification.objects.filter(
        is_active=True,
        require_acknowledgement=True,  # optional filter
        scheduled_for__lt=now(),  # already sent
        expired_at__isnull=True,
    )
    count = expired.count()

    for broadcast in expired:
        broadcast.is_active = False
        broadcast.expired_at = now()
        broadcast.save(update_fields=['is_active', 'expired_at'])


@shared_task
def delete_old_expired_broadcasts():
    """Delete broadcasts that have been expired for more than 90 days"""
    cutoff = now() - timedelta(days=90)
    BroadcastNotification.objects.filter(
        expired_at__lt=cutoff
    ).delete()