"""
Celery tasks for announcements app.
"""
from celery import shared_task
from django.utils import timezone
from django.db import connection
from notifications_system.services.broadcast_services import BroadcastNotificationService
from .models import Announcement
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, ignore_result=True)
def send_scheduled_announcements(self):
    """
    Send announcements that are scheduled for the current time or earlier.
    Runs periodically via Celery Beat.
    """
    try:
        # Ensure database connection is available
        connection.ensure_connection()
    except Exception as e:
        logger.warning(f"Database connection issue in send_scheduled_announcements: {e}. Will retry later.")
        # Don't retry immediately - let the next scheduled run handle it
        return f"Skipped due to database connection issue: {e}"
    
    try:
        now = timezone.now()
        
        # Find announcements scheduled for now or earlier that haven't been sent
        scheduled_announcements = Announcement.objects.filter(
            broadcast__scheduled_for__lte=now,
            broadcast__sent_at__isnull=True,
            broadcast__is_active=True
        ).select_related('broadcast')

        sent_count = 0
        for announcement in scheduled_announcements:
            try:
                broadcast = announcement.broadcast
                
                # Send the broadcast
                BroadcastNotificationService.send_broadcast(
                    event=broadcast.event_type,
                    title=broadcast.title,
                    message=broadcast.message,
                    website=broadcast.website,
                    channels=broadcast.channels or ['in_app', 'email'],
                    is_test=False
                )
                
                # Mark as sent
                broadcast.sent_at = timezone.now()
                broadcast.save(update_fields=['sent_at'])
                
                sent_count += 1
                logger.info(f"Sent scheduled announcement: {announcement.id}")
                
            except Exception as e:
                logger.error(f"Failed to send scheduled announcement {announcement.id}: {e}", exc_info=True)

        return f"Sent {sent_count} scheduled announcement(s)"
    except Exception as e:
        logger.error(f"Error in send_scheduled_announcements task: {e}", exc_info=True)
        # Don't retry on general errors, just log
        return f"Error processing scheduled announcements: {e}"


@shared_task(bind=True, max_retries=3, ignore_result=True)
def expire_announcements(self):
    """
    Deactivate announcements that have expired.
    Runs periodically via Celery Beat.
    """
    try:
        # Ensure database connection is available
        connection.ensure_connection()
    except Exception as e:
        logger.warning(f"Database connection issue in expire_announcements: {e}. Will retry later.")
        # Don't retry immediately - let the next scheduled run handle it
        return f"Skipped due to database connection issue: {e}"
    
    try:
        now = timezone.now()
        
        expired = Announcement.objects.filter(
            broadcast__expires_at__lte=now,
            broadcast__is_active=True
        ).select_related('broadcast')

        count = 0
        for announcement in expired:
            try:
                announcement.broadcast.is_active = False
                announcement.broadcast.save(update_fields=['is_active'])
                count += 1
            except Exception as e:
                logger.error(f"Failed to expire announcement {announcement.id}: {e}", exc_info=True)

        return f"Expired {count} announcement(s)"
    except Exception as e:
        logger.error(f"Error in expire_announcements task: {e}", exc_info=True)
        # Don't retry on general errors, just log
        return f"Error expiring announcements: {e}"

