from .base import BaseDeliveryBackend
import logging

logger = logging.getLogger(__name__)


class InAppBackend(BaseDeliveryBackend):
    """
    Marks the notification as deliverable via in-app UI.
    Optionally logs the delivery for tracking, auditing, or analytics.
    """

    def send(self):
        try:
            self.notification.status = "sent"
            self.notification.save(update_fields=["status"])

            self._log_delivery(success=True)
            return True

        except Exception as e:
            logger.exception(
                "Failed to mark in-app notification as sent",
                extra={
                    "notification_id": self.notification.id,
                    "user_id": getattr(self.notification.user, "id", None),
                    "channel": "in_app",
                }
            )
            self._log_delivery(success=False)
            return False

    def _log_delivery(self, success: bool):
        """
        Optional hook to track in-app delivery for auditing, retries, analytics, etc.
        """
        from notifications_system.models.notification_log import NotificationLog
        NotificationLog.objects.create(
            notification=self.notification,
            channel="in_app",
            success=success,
            user=self.notification.user,
            website=self.notification.website,
            payload=self.notification.payload or {},
            config=self.channel_config or {},
            message=self.notification.message,
            title=self.notification.title,
            html_message=self.channel_config.get("html_message", None)
        )

    def supports_retry(self):
        return False  # No retry necessary for in-app tagging
