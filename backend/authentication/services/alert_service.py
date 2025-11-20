import requests
from django.conf import settings


class AdminAlertService:
    """Sends webhook alerts to administrators for suspicious activity."""

    @staticmethod
    def send_suspicious_login_alert(user, ip, reason, website):
        """
        Sends a webhook alert for suspicious login activity.

        Args:
            user (User): The user who triggered the alert.
            ip (str): The IP address of the suspicious login.
            reason (str): Reason for triggering the alert.
            website (Website): Tenant site context.
        """
        payload = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "ip": ip,
            "reason": reason,
            "website_id": website.id,
            "website_name": website.name,
        }
        webhook_url = getattr(settings, "ADMIN_ALERT_WEBHOOK_URL", None)
        if webhook_url:
            try:
                requests.post(webhook_url, json=payload, timeout=3)
            except requests.RequestException:
                pass  # Silently fail to avoid interrupting login