from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from django.conf import settings

class SuspiciousLoginAlertService:
    @staticmethod
    def send_alert(user, login_session, geo_location="Unknown"):
        """
        Sends an email alert for suspicious login.

        Args:
            user (User): The user who logged in.
            login_session (LoginSession): The session triggering the alert.
            geo_location (str): Optional location info from IP (e.g. "Nairobi, KE").
        """
        subject = "⚠️ Suspicious Login Detected"
        context = {
            "user": user,
            "ip_address": login_session.ip_address,
            "user_agent": login_session.user_agent,
            "timestamp": localtime(login_session.logged_in_at),
            "geo_location": geo_location
        }

        message = render_to_string("emails/suspicious_login.txt", context)
        html_message = render_to_string("emails/suspicious_login.html", context)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message
        )