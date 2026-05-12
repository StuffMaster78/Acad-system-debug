from __future__ import annotations

from django.conf import settings
from django.db import models

from typing import TYPE_CHECKING

from decimal import Decimal
from websites.models.websites import Website
from writer_compensation.enums.compensation_enums import (
    PayoutBatchStatus,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from writer_compensation.models.payout_record import PayoutRecord

User = settings.AUTH_USER_MODEL


class PayoutBatch(models.Model):
    """
    High level payout grouping for a compensation window.
    One batch per window (OneToOne). Admin-managed.

    Created automatically when a window is CLOSED.
    total_amount is denormalised and informational only 
    — the authoritative total is always the sum of
      confirmed PayoutItems.

    Example:
        May Biweekly Payout Batch
        → contains all writer payout records (items)
    """
    records: QuerySet[PayoutRecord]

    website = models.ForeignKey(
        Website,
        on_delete=models.PROTECT,
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
        "writer_compensation.PaymentWindow",
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
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_payout_batches",
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payout_batches",
    )

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["payment_window"]),
        ]

    def __str__(self):
        return (
            f"Batch {self.pk} | window {self.payment_window.pk}"
            f"status {self.status} | Total Amount: {self.total_amount}"
        )
