from .base import BaseDeliveryBackend
import logging

logger = logging.getLogger(__name__)

class PushBackend(BaseDeliveryBackend):
    """
    Sends push notifications to mobile/web apps via FCM, OneSignal, etc.
    """

    def send(self):
        user = self.notification.user
        payload = self.notification.payload or {}

        logger.info(f"[Push] Sending push to {user}: {payload}")
        # Integrate push provider logic here
        return True

    def supports_retry(self):
        return True