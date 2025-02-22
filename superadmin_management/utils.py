from django.core.mail import send_mail
from django.conf import settings
from notifications_system.models import Notification
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from superadmin_management.tasks import send_email_task  # Celery task for email retry
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SuperadminNotifier:
    """Handles Superadmin notifications via email, in-app alerts, and WebSockets."""

    @staticmethod
    def notify_superadmins(title, message, category="general"):
        """Sends notifications via WebSocket, email (with retry), and in-app alerts."""
        superadmins = User.objects.filter(role="superadmin")

        if not superadmins.exists():
            logger.warning("No Superadmins found to notify.")
            return

        recipient_emails = []

        for superadmin in superadmins:
            # In-App Notification
            Notification.objects.create(
                user=superadmin,
                title=title,
                message=message,
                category=category
            )

            # Collect emails for batch email sending
            if superadmin.email:
                recipient_emails.append(superadmin.email)

        # Send Email via Celery Task (Retries on Failure)
        if recipient_emails:
            send_email_task.delay(
                subject=f"Superadmin Alert: {title}",
                message=message,
                recipient_list=recipient_emails
            )

        # Send WebSocket Notification
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "superadmin_notifications",
                {"type": "send_notification", "message": {"title": title, "message": message}}
            )
        except Exception as e:
            logger.error(f"WebSocket notification failed: {e}")