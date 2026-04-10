from django.db import models

from payments_processor.constants import DEFAULT_CURRENCY
from payments_processor.enums import (
    PaymentTransactionKind,
    PaymentTransactionStatus,
)


class PaymentTransaction(models.Model):
    """
    Stores provider transaction events and verification facts.
    """

    payment_intent = models.ForeignKey(
        "payments.PaymentIntent",
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    provider = models.CharField(max_length=32)

    kind = models.CharField(
        max_length=32,
        choices=PaymentTransactionKind.choices,
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentTransactionStatus.choices,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=10,
        default=DEFAULT_CURRENCY,
    )

    provider_transaction_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )

    provider_event_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )

    failure_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )

    failure_message = models.TextField(blank=True, default="")
    raw_payload = models.JSONField(default=dict, blank=True)

    occurred_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["provider", "provider_event_id"]),
            models.Index(fields=["provider", "provider_transaction_id"]),
            models.Index(fields=["payment_intent", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_intent.reference} {self.kind}"