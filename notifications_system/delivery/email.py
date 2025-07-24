from .base import BaseDeliveryBackend
from notifications_system.utils.email_helpers import send_website_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


class EmailBackend(BaseDeliveryBackend):
    """
    Sends email notifications via the tenant-aware email utility.
    Supports optional template rendering, HTML messages, and overrides.
    """

    def send(self):
        user = self.notification.user
        website = self.notification.website
        payload = self.notification.payload or {}
        config = self.channel_config or {}

        try:
            context = {
                "user": user,
                "notification": self.notification,
                **payload
            }

            # Optional template rendering
            html_message = None
            template = config.get("template")

            if template:
                html_message = render_to_string(template, context)
            elif config.get("html_message"):
                html_message = config["html_message"]

            subject = payload.get("title") or self.notification.title
            message = payload.get("message") or self.notification.message
            recipient_email = config.get("email_override") or user.email

            send_website_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                recipient_list=[recipient_email],
                website=website,
            )

            self._log_delivery(success=True)
            return True

        except Exception as e:
            logger.exception(
                "EmailBackend failed to send notification",
                extra={
                    "user_id": getattr(user, "id", None),
                    "email": getattr(user, "email", None),
                    "notification_id": self.notification.id,
                    "channel": "email"
                }
            )
            self._log_delivery(success=False)
            return False

    def supports_retry(self):
        return True

    def _log_delivery(self, success: bool):
        """
        Optional hook: log notification delivery attempt for auditing/retries.
        You can implement this method to store delivery results.
        """
        from notifications_system.models.notification_log import NotificationLog
        
        NotificationLog.objects.create(
            notification=self.notification,
            channel="email",
            success=success,
            user=self.notification.user,
            website=self.notification.website,
            payload=self.notification.payload or {},
            config=self.channel_config or {},
            message=self.notification.message,
            title=self.notification.title,
            html_message=self.channel_config.get("html_message", None)
        )
