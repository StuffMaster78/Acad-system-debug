from .base import BaseDeliveryBackend
import logging

logger = logging.getLogger(__name__)

class SMSBackend(BaseDeliveryBackend):
    """
    Sends SMS notifications. Integrate Twilio or any other SMS service here.
    """

    def send(self):
        phone = getattr(self.notification.user.profile, "phone_number", None)
        if not phone:
            logger.warning(f"No phone number found for user {self.notification.user}")
            return False

        # Dummy logic — Replace with Twilio or any provider
        logger.info(f"Sending SMS to {phone}: {self.notification.payload.get('message')}")
        return True

    def supports_retry(self):
        return True