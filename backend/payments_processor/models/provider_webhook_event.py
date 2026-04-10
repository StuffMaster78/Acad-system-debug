from django.db import models

from payments_processor.enums import WebhookProcessingStatus


class ProviderWebhookEvent(models.Model):
    """
    Stores raw inbound webhook events for audit and idempotency.
    """

    provider = models.CharField(max_length=32)

    event_id = models.CharField(max_length=128)
    event_type = models.CharField(max_length=128, blank=True, default="")

    payment_intent = models.ForeignKey(
        "payments.PaymentIntent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="webhook_events",
    )

    signature_verified = models.BooleanField(default=False)

    payload = models.JSONField(default=dict, blank=True)

    processing_status = models.CharField(
        max_length=32,
        choices=WebhookProcessingStatus.choices,
        default=WebhookProcessingStatus.RECEIVED,
    )

    error_message = models.TextField(blank=True, default="")

    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "event_id"],
                name="unique_provider_webhook_event",
            )
        ]
        indexes = [
            models.Index(fields=["provider", "event_type"]),
            models.Index(fields=["processing_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.event_id}"