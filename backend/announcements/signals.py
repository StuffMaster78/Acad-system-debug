"""
Signals for announcements app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from notifications_system.models.broadcast_notification import BroadcastNotification
from notifications_system.services.broadcast_services import BroadcastNotificationService
from .models import Announcement
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BroadcastNotification)
def create_announcement_from_broadcast(sender, instance, created, **kwargs):
    """
    Automatically create an Announcement when a BroadcastNotification
    is created with event_type starting with 'announcement.' or 'broadcast.'
    """
    if created and instance.event_type.startswith(('announcement.', 'broadcast.')):
        # Only create if announcement doesn't already exist
        if not hasattr(instance, 'announcement'):
            Announcement.objects.create(
                broadcast=instance,
                category='general'
            )


@receiver(post_save, sender=Announcement)
def send_announcement_notifications(sender, instance, created, **kwargs):
    """
    Send email notifications when a new announcement is created.
    """
    if created and instance.broadcast:
        try:
            # Only send if announcement is active and should send email
            if instance.broadcast.is_active and 'email' in (instance.broadcast.channels or []):
                # The broadcast system will handle sending via NotificationService
                # We just need to ensure the broadcast is sent
                if not instance.broadcast.sent_at:
                    # Send the broadcast which will trigger email notifications
                    BroadcastNotificationService.send_broadcast(
                        event=instance.broadcast.event_type,
                        title=instance.broadcast.title,
                        message=instance.broadcast.message,
                        website=instance.broadcast.website,
                        channels=instance.broadcast.channels or ['in_app', 'email'],
                        is_test=False
                    )
                    instance.broadcast.sent_at = timezone.now()
                    instance.broadcast.save(update_fields=['sent_at'])
        except Exception as e:
            logger.error(f"Failed to send announcement notifications: {e}", exc_info=True)
