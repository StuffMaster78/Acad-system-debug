from django.conf import settings
from django.db import models

class RateLimitEvent(models.Model):
    """
    Record rate-limit events for security-sensitive actions such as
    login attempts and magic link requests.
    """
    class Reason(models.TextChoices):
        LOGIN_THROTTLE = "login_throttle", "Login Throttle"
        MAGIC_LINK_THROTTLE = "magic_link_throttle", "Magic Link Throttle"
        MFA_THROTTLE = "mfa_throttle", "MFA Throttle"
        PASSWORD_RESET_THROTTLE = (
            "password_reset_throttle",
            "Password Reset Throttle",
        )
        LOGOUT_ALL_SESSIONS_THROTTLE = (
            "logout_all_sessions_throttle",
            "Logout All Sessions Throttle",
        )
        DEVICE_RISK_THROTTLE = (
            "device_risk_throttle",
            "Device Risk Throttle",
        )
        UNKNOWN = "unknown", "Unknown"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rate_limit_events",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="rate_limit_events",
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(
        null=True,
        blank=True,
    )
    path = models.CharField(
        max_length=255,
    )
    method = models.CharField(
        max_length=10,
    )
    triggered_at = models.DateTimeField(
        auto_now_add=True,
    )
    metadata = models.JSONField(default=dict, blank=True)
    reason = models.CharField(
        max_length=64,
        choices=Reason.choices,
        default=Reason.LOGIN_THROTTLE,
    )

    class Meta:
        ordering = ["-triggered_at"]
        indexes = [
            models.Index(fields=["website", "ip_address", "triggered_at"]),
            models.Index(fields=["user", "triggered_at"]),
            models.Index(fields=["reason", "triggered_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the rate-limit event.
        """
        return (
            f"[{self.website}] {self.ip_address} "
            f"({self.reason})"
        )