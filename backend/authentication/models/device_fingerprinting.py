from django.conf import settings
from django.db import models
from django.utils import timezone


class DeviceFingerprint(models.Model):
    """
    Represent a device or browser fingerprint associated with a user.

    This model stores fingerprint data used for trust decisions,
    session validation, anomaly detection, and risk analysis.

    Notes:
        - `fingerprint_hash` should be derived outside the model.
        - Risk scoring logic should live in a service layer.
        - This model stores state, not the full fraud engine.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_fingerprints",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="device_fingerprints",
    )
    fingerprint_hash = models.CharField(
        max_length=255,
        help_text=(
            "Hash of the device fingerprint, such as one generated "
            "by a browser fingerprinting library."
        ),
    )
    user_agent = models.TextField(
        help_text="Full user agent string for the client device.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        help_text="IP address associated with this fingerprint.",
    )
    is_trusted = models.BooleanField(
        default=False,
        help_text="Whether this fingerprint is currently trusted.",
    )
    trust_score = models.FloatField(
        default=0.0,
        help_text="Computed trust score for this fingerprint.",
    )
    device_name = models.TextField(
        null=True,
        help_text="The name of device being fingerprinted.",
    )
    login_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of successful logins associated with this fingerprint.",
    )
    last_seen_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this fingerprint was last observed.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this fingerprint was first recorded.",
    )

    class Meta:
        ordering = ["-last_seen_at"]
        verbose_name = "Device Fingerprint"
        verbose_name_plural = "Device Fingerprints"
        indexes = [
            models.Index(fields=["user", "website"]),
            models.Index(fields=["website", "fingerprint_hash"]),
            models.Index(fields=["is_trusted", "last_seen_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website", "fingerprint_hash"],
                name="unique_fingerprint_per_user_per_website",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the fingerprint.
        """
        trust_status = "trusted" if self.is_trusted else "untrusted"
        return (
            f"Fingerprint for {self.user} "
            f"on {self.website} ({trust_status})"
        )

    def is_stale(self, *, hours: int = 48) -> bool:
        """
        Determine whether this fingerprint is stale.

        Args:
            hours: Maximum allowed age in hours before the fingerprint
                is considered stale.

        Returns:
            True if the fingerprint is older than the given threshold,
            otherwise False.
        """
        threshold = timezone.now() - timezone.timedelta(hours=hours)
        return self.last_seen_at < threshold

    def mark_as_trusted(self) -> None:
        """
        Mark this fingerprint as trusted.
        """
        if not self.is_trusted:
            self.is_trusted = True
            self.save(update_fields=["is_trusted", "last_seen_at"])

    def mark_as_untrusted(self) -> None:
        """
        Mark this fingerprint as untrusted.
        """
        if self.is_trusted:
            self.is_trusted = False
            self.save(update_fields=["is_trusted", "last_seen_at"])

    def record_login(self) -> None:
        """
        Increment the login count and refresh the last-seen timestamp.
        """
        self.login_count += 1
        self.save(update_fields=["login_count", "last_seen_at"])