from django.db import models

from payments_processor.constants import DEFAULT_CURRENCY
from payments_processor.enums import PaymentRefundStatus, RefundDestination


class PaymentRefund(models.Model):
    """
    Represents a payment-side refund execution record.
    This tracks refund execution on the gateway side.
    """

    payment_intent = models.ForeignKey(
        "payments.PaymentIntent",
        on_delete=models.PROTECT,
        related_name="refunds",
    )

    payment_transaction = models.ForeignKey(
        "payments.PaymentTransaction",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="refunds",
    )

    provider = models.CharField(max_length=32)
    provider_refund_id = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )

    destination = models.CharField(
        max_length=32,
        choices=RefundDestination.choices,
        default=RefundDestination.ORIGINAL_METHOD,
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentRefundStatus.choices,
        default=PaymentRefundStatus.REQUESTED,
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(
        max_length=10,
        default=DEFAULT_CURRENCY,
    )

    failure_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )
    failure_message = models.TextField(blank=True, default="")

    raw_payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["payment_intent", "requested_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["provider", "provider_refund_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_intent.reference}:{self.amount}"