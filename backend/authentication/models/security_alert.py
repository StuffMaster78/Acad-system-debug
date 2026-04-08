from django.conf import settings
from django.db import models
from django.utils import timezone


class LoginAlert(models.Model):
    """
    Represents a login-related security event for a user.

    Used for:
    - notifying users of new or suspicious logins
    - tracking login activity beyond generic audit logs
    - supporting security monitoring and alerting

    This is NOT a session model.
    """

    class AlertType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login Success"
        LOGIN_FAILED = "login_failed", "Login Failed"
        NEW_DEVICE = "new_device", "New Device Login"
        SUSPICIOUS_LOGIN = "suspicious_login", "Suspicious Login"
        MFA_REQUIRED = "mfa_required", "MFA Required"
        MFA_FAILED = "mfa_failed", "MFA Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_alerts",
    )

    # What happened
    alert_type = models.CharField(
        max_length=50,
        choices=AlertType.choices,
    )

    # Context (important for security analysis)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
    )

    device_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional parsed device name (e.g. Chrome on Mac)",
    )

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Approximate location (e.g. Nairobi, Kenya)",
    )

    # Extra metadata (flexible, future-proof)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context for the alert",
    )

    # Delivery tracking (optional but useful)
    is_notified = models.BooleanField(
        default=False,
        help_text="Whether notification has been sent",
    )

    notified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["alert_type"]),
        ]

    def mark_notified(self):
        """Mark alert as notified."""
        self.is_notified = True
        self.notified_at = timezone.now()
        self.save(update_fields=["is_notified", "notified_at"])

    def __str__(self):
        return f"{self.user} - {self.alert_type} @ {self.created_at}"
    