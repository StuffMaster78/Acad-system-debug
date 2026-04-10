from django.db import models

from payments_processor.constants import DEFAULT_CURRENCY
from payments_processor.enums import PaymentDisputeStatus


class PaymentDispute(models.Model):
    """
    Represents a provider dispute or chargeback case.
    """

    payment_intent = models.ForeignKey(
        "payments.PaymentIntent",
        on_delete=models.PROTECT,
        related_name="disputes",
    )

    payment_transaction = models.ForeignKey(
        "payments.PaymentTransaction",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="disputes",
    )

    provider = models.CharField(max_length=32)
    provider_dispute_id = models.CharField(max_length=128)

    status = models.CharField(
        max_length=32,
        choices=PaymentDisputeStatus.choices,
        default=PaymentDisputeStatus.OPEN,
    )

    reason = models.CharField(max_length=255, blank=True, default="")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(
        max_length=10,
        default=DEFAULT_CURRENCY,
    )

    opened_at = models.DateTimeField()
    due_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    raw_payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_dispute_id"],
                name="unique_provider_dispute",
            )
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["payment_intent", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_dispute_id}"