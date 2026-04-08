from django.db import models
from django.utils.translation import gettext_lazy as _


class SecurityEvent(models.Model):
    """
    Store security-relevant events for audit trails, user transparency,
    and operational review.
    """

    class EventType(models.TextChoices):
        LOGIN = "login", _("Login")
        LOGIN_FAILED = "login_failed", _("Failed Login")
        LOGOUT = "logout", _("Logout")
        PASSWORD_CHANGE = "password_change", _("Password Changed")
        PASSWORD_RESET = "password_reset", _("Password Reset")
        TWO_FA_ENABLED = "2fa_enabled", _("2FA Enabled")
        TWO_FA_DISABLED = "2fa_disabled", _("2FA Disabled")
        TWO_FA_VERIFIED = "2fa_verified", _("2FA Verified")
        MAGIC_LINK_USED = "magic_link_used", _("Magic Link Used")
        DEVICE_TRUSTED = "device_trusted", _("Device Trusted")
        DEVICE_REVOKED = "device_revoked", _("Device Revoked")
        SESSION_CREATED = "session_created", _("Session Created")
        SESSION_REVOKED = "session_revoked", _("Session Revoked")
        SUSPICIOUS_ACTIVITY = "suspicious_activity", _(
            "Suspicious Activity"
        )
        SUSPICIOUS_SESSION_REPORTED = (
            "suspicious_session_reported",
            _("Suspicious Session Reported"),
        )
        ACCOUNT_LOCKED = "account_locked", _("Account Locked")
        ACCOUNT_UNLOCKED = "account_unlocked", _("Account Unlocked")
        PROFILE_UPDATED = "profile_updated", _("Profile Updated")
        PRIVACY_SETTINGS_CHANGED = (
            "privacy_settings_changed",
            _("Privacy Settings Changed"),
        )

    class Severity(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="security_events",
        help_text=_("User this event belongs to."),
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="security_events",
        help_text=_("Website this event occurred on."),
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        help_text=_("Type of security event."),
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.LOW,
        help_text=_("Severity of the event."),
    )
    is_suspicious = models.BooleanField(
        default=False,
        help_text=_("Whether this event is suspicious."),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("IP address associated with the event."),
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Geographic location summary."),
    )
    device = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Device information."),
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text=_("User agent string."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the event occurred."),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional event metadata."),
    )

    class Meta:
        verbose_name = _("Security Event")
        verbose_name_plural = _("Security Events")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["website", "-created_at"]),
            models.Index(fields=["user", "event_type", "-created_at"]),
            models.Index(fields=["event_type", "-created_at"]),
            models.Index(fields=["is_suspicious", "-created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the event.
        """
        return (
            f"{self.user.email} | {self.event_type} | "
            f"{self.created_at:%Y-%m-%d %H:%M:%S}"
        )

    @classmethod
    def log_event(
        cls,
        *,
        user,
        website,
        event_type: str,
        severity: str = Severity.LOW,
        is_suspicious: bool = False,
        ip_address: str | None = None,
        location: str | None = None,
        device: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
    ):
        """
        Create a security event entry.

        Args:
            user: User instance.
            website: Website instance.
            event_type: Security event type.
            severity: Event severity.
            is_suspicious: Whether event is suspicious.
            ip_address: Optional IP address.
            location: Optional location string.
            device: Optional device info.
            user_agent: Optional user agent string.
            metadata: Optional event metadata.

        Returns:
            Created SecurityEvent instance.
        """
        return cls.objects.create(
            user=user,
            website=website,
            event_type=event_type,
            severity=severity,
            is_suspicious=is_suspicious,
            ip_address=ip_address,
            location=location,
            device=device,
            user_agent=user_agent,
            metadata=metadata or {},
        )