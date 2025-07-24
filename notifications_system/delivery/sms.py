from .base import BaseDeliveryBackend
from notifications_system.utils.sms_helpers import send_sms_notification
import logging

logger = logging.getLogger(__name__)


class SMSBackend(BaseDeliveryBackend):
    """
    Sends SMS notifications via a pluggable utility function.
    This could wrap Twilio, Africa's Talking, or other providers.
    """

    def send(self):
        user = self.notification.user
        payload = self.notification.payload or {}
        config = self.channel_config or {}

        phone = getattr(getattr(user, "profile", None), "phone_number", None)
        if not phone:
            logger.warning(f"[SMS] No phone number found for user {user.id}")
            return False

        try:
            message = payload.get("message") or self.notification.message
            success = send_sms_notification(phone, message, config=config)

            if not success:
                logger.warning(f"[SMS] Delivery failed to {phone}")
            return success

        except Exception as e:
            logger.error(f"[SMS] Exception while sending SMS to {phone}: {e}", exc_info=True)
            return False

    def supports_retry(self):
        return True
