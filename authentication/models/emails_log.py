"""
Model for logging authentication-related
email notifications sent to users.
"""

from django.db import models
from django.conf import settings


class EmailNotificationLog(models.Model):
    """
    Records security emails sent to a user
    (e.g., password changes, login alerts)
    per website (tenant).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_logs"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="email_logs"
    )
    event = models.CharField(
        max_length=128,
        help_text=(
            "Type of email event, e.g., 'password_reset', 'login_alert'"
        )
    )
    recipient_email = models.EmailField(
        help_text="Email address to which the notification was sent"
    )
    message_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=(
            "Optional email service provider message ID for tracking"
        )
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.event} to {self.recipient_email} "
            f"at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
        )