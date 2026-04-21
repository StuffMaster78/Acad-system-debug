from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from payments_processor.constants import DEFAULT_CURRENCY, ZERO_DECIMAL
from payments_processor.enums import (
    PaymentTransactionKind,
    PaymentTransactionStatus,
)


class PaymentTransaction(models.Model):
    """
    Provider transaction or event history for a payment intent.
    One payment intent may have many transactions or events.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.PROTECT,
        related_name="payment_transactions",
    )
    payment_intent = models.ForeignKey(
        "payments_processor.PaymentIntent",
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

    occurred_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "payment_intent", "created_at"]),
            models.Index(fields=["provider", "provider_event_id"]),
            models.Index(fields=["provider", "provider_transaction_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["kind"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_intent.reference} {self.kind}"