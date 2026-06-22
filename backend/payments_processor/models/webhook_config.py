from django.db import models


class WebhookConfig(models.Model):
    """
    Runtime configuration for outbound and inbound webhook behaviour.
    One global row (no website FK — webhook behaviour is platform-wide).
    """

    retry_attempts = models.PositiveSmallIntegerField(
        default=3,
        help_text="How many times a failed webhook delivery is retried.",
    )
    timeout_seconds = models.PositiveSmallIntegerField(
        default=30,
        help_text="Maximum seconds to wait for a webhook endpoint to respond.",
    )
    signature_verification_enabled = models.BooleanField(
        default=True,
        help_text="Verify HMAC signatures on inbound webhook payloads.",
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhook_config_updates",
    )

    class Meta:
        verbose_name = "Webhook Config"
        verbose_name_plural = "Webhook Config"

    def __str__(self) -> str:
        return (
            f"WebhookConfig(retry={self.retry_attempts}, "
            f"timeout={self.timeout_seconds}s, "
            f"sig={'on' if self.signature_verification_enabled else 'off'})"
        )

    @classmethod
    def get(cls) -> "WebhookConfig":
        """Return the single config row, creating it with defaults if absent."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
