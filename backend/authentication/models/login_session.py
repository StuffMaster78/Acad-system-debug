from django.conf import settings
from django.db import models
from django.utils.timezone import now


class LoginSession(models.Model):
    """
    Represent a user's authenticated session on a website.

    This model stores session metadata such as:
        - user and website context
        - device and network information
        - session lifecycle timestamps
        - hashed session token
        - optional device fingerprint linkage
    """

    class SessionType(models.TextChoices):
        PASSWORD = "password", "Password Login"
        MAGIC_LINK = "magic_link", "Magic Link"
        MFA = "mfa", "MFA"
        IMPERSONATION = "impersonation", "Impersonation"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_sessions",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="login_sessions",
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="Hashed session token.",
    )
    session_type = models.CharField(
        max_length=30,
        choices=SessionType.choices,
        default=SessionType.PASSWORD,
        help_text="How this session was authenticated.",
    )
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
    )
    fingerprint_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Associated device fingerprint hash, if available.",
    )
    logged_in_at = models.DateTimeField(
        default=now,
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Absolute expiry for this login session.",
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revoked_sessions",
    )

    class Meta:
        ordering = ["-logged_in_at"]
        indexes = [
            models.Index(fields=["user", "website"]),
            models.Index(fields=["token_hash"]),
            models.Index(fields=["fingerprint_hash"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_active(self) -> bool:
        """
        Return whether this session is currently valid.

        A session is active if:
            - it has not been revoked
            - it has not expired
        """
        if self.revoked_at is not None:
            return False

        if self.expires_at is not None and now() >= self.expires_at:
            return False

        return True

    def revoke(self, revoked_by=None) -> None:
        """
        Revoke this session.

        Args:
            revoked_by: Optional user who revoked the session.
        """
        if self.revoked_at is None:
            self.revoked_at = now()

        if revoked_by is not None:
            self.revoked_by = revoked_by

        self.save(update_fields=["revoked_at", "revoked_by"])

    def touch(self) -> None:
        """
        Update the last activity timestamp for this session.
        """
        self.last_activity_at = now()
        self.save(update_fields=["last_activity_at"])

    def __str__(self) -> str:
        """
        Return a human-readable session summary.
        """
        return (
            f"{self.user} | {self.website} | "
            f"{self.ip_address or 'unknown_ip'} | "
            f"{self.session_type}"
        )