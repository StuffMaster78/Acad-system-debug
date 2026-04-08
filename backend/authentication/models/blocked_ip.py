from django.db import models
from django.utils import timezone


class BlockedIP(models.Model):
    """
    Represent an IP address that is temporarily blocked for a specific
    website due to suspicious or abusive authentication activity.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="blocked_ips",
    )
    ip_address = models.GenericIPAddressField(
        help_text="Blocked IP address.",
    )
    blocked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the IP was blocked.",
    )
    blocked_until = models.DateTimeField(
        help_text="Timestamp until which the IP remains blocked.",
    )

    class Meta:
        ordering = ["-blocked_until"]
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"
        constraints = [
            models.UniqueConstraint(
                fields=["website", "ip_address"],
                name="unique_blocked_ip_per_website",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "ip_address"]),
            models.Index(fields=["blocked_until"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the blocked IP.
        """
        return (
            f"Blocked IP {self.ip_address} "
            f"for {self.website} until {self.blocked_until}"
        )

    @property
    def is_active(self) -> bool:
        """
        Return whether the IP block is still active.
        """
        return timezone.now() < self.blocked_until