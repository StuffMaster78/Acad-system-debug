from .base import BaseDeliveryBackend
from notifications_system.utils.email_helpers import send_website_mail
  

class EmailBackend(BaseDeliveryBackend):
    """
    Sends email notifications via the tenant-aware email utility.
    """

    def send(self):
        user = self.notification.user
        website = self.notification.website
        payload = self.notification.payload or {}
        config = self.channel_config

        return send_website_mail(
            subject=payload.get("title", self.notification.title),
            message=payload.get("message", self.notification.message),
            html_message=config.get("html_message"),
            recipient_list=[config.get("email_override") or user.email],
            website=website
        )

    def supports_retry(self):
        return True
