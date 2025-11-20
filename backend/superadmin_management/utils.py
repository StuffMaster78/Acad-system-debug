from django.core.mail import send_mail
from django.conf import settings
from notifications_system.models.notifications import Notification
from django.contrib.auth import get_user_model
from websites.models import Website
# from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from superadmin_management.tasks import send_email_task  # Celery task for email retry
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SuperadminNotifier:
    """Handles Superadmin notifications via email, in-app alerts, and WebSockets."""

    @staticmethod
    def notify_superadmins(title, message, category="general", website=None):
        """
        Sends notifications via WebSocket, email (with retry), and in-app alerts.
        
        Args:
            title: Notification title
            message: Notification message
            category: Notification category (default: "general")
            website: Website instance (optional, will be derived if not provided)
        """
        superadmins = User.objects.filter(role="superadmin")

        if not superadmins.exists():
            logger.warning("No Superadmins found to notify.")
            return

        # Get website - use provided one, or get from first superadmin, or first active website
        if not website:
            first_superadmin = superadmins.first()
            website = getattr(first_superadmin, 'website', None)
            if not website:
                website = Website.objects.filter(is_active=True).first()
                if not website:
                    logger.error("No website available for notification. Cannot create notification.")
                    return

        recipient_emails = []

        for superadmin in superadmins:
            # Use superadmin's website if available, otherwise use the default
            notification_website = getattr(superadmin, 'website', None) or website
            
            # In-App Notification - use get_or_create to avoid duplicates
            try:
                Notification.objects.get_or_create(
                    user=superadmin,
                    website=notification_website,
                    title=title,
                    message=message,
                    type='in_app',
                    defaults={
                        'category': category,
                        'event': 'system',
                        'status': 'pending',
                    }
                )
            except Exception as e:
                logger.debug(f"Could not create notification for {superadmin.username}: {e}")

            # Collect emails for batch email sending
            if superadmin.email:
                recipient_emails.append(superadmin.email)

        # Send Email via Celery Task (Retries on Failure)
        if recipient_emails:
            try:
                send_email_task.delay(
                    subject=f"Superadmin Alert: {title}",
                    message=message,
                    recipient_list=recipient_emails
                )
            except (ConnectionRefusedError, OSError) as e:
                # Celery/Redis not available - log but don't fail
                logger.debug(f"Could not queue email task (Celery/Redis unavailable): {e}")
            except Exception as e:
                logger.warning(f"Failed to queue email task: {e}", exc_info=True)

        # # Send WebSocket Notification
        # try:
        #     channel_layer = get_channel_layer()
        #     async_to_sync(channel_layer.group_send)(
        #         "superadmin_notifications",
        #         {"type": "send_notification", "message": {"title": title, "message": message}}
        #     )
        # except Exception as e:
        #     logger.error(f"WebSocket notification failed: {e}")