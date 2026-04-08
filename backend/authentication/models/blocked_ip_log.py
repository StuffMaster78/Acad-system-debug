from django.db import models


class BlockedIPLog(models.Model):
    """
    Represent a historical record of an IP block event for a website.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="blocked_ip_logs",
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address that was blocked.",
    )
    reason = models.TextField(
        help_text="Reason the IP address was blocked.",
    )
    blocked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the block was recorded.",
    )
    duration_minutes = models.PositiveIntegerField(
        help_text="Duration of the block in minutes.",
    )

    class Meta:
        ordering = ["-blocked_at"]
        verbose_name = "Blocked IP Log"
        verbose_name_plural = "Blocked IP Logs"
        indexes = [
            models.Index(fields=["website", "ip_address"]),
            models.Index(fields=["blocked_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the blocked IP log.
        """
        return (
            f"Blocked IP log for {self.ip_address} "
            f"on {self.website}"
        )