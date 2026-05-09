from __future__ import annotations

from django.conf import settings
from django.db import models

from decimal import Decimal
from websites.models.websites import Website
from writer_payments_management.enums.financial_event_enums import (
    PayoutBatchStatus,
)


User = settings.AUTH_USER_MODEL


class PayoutBatch(models.Model):
    """
    High level payout grouping for a payment window.

    Example:
        May Biweekly Payout Batch
        → contains all writer payout records
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="payout_batches",
    )

    title = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=32,
        choices=PayoutBatchStatus.choices,
        default=PayoutBatchStatus.DRAFT,
    )

    payment_window = models.ForeignKey(
        "writer_payments_management.PaymentWindow",
        on_delete=models.CASCADE,
        related_name="payout_batches",
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_writers = models.PositiveIntegerField(
        default=0,
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payout_batches",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} | {self.status}"