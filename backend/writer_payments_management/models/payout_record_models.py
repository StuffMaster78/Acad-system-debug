from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website
from writer_payments_management.enums.financial_event_enums import (
    PayoutRecordStatus,
)


User = settings.AUTH_USER_MODEL


class PayoutRecord(models.Model):
    """
    Per writer payout instruction inside a batch.

    This is NOT money movement.
    This is "intent to pay".
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="payout_records",
    )

    batch = models.ForeignKey(
        "writer_payments_management.PayoutBatch",
        on_delete=models.CASCADE,
        related_name="records",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="payout_records",
    )

    settlement_period = models.ForeignKey(
        "writer_payments_management.SettlementPeriod",
        on_delete=models.CASCADE,
        related_name="payout_records",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    external_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=32,
        choices=PayoutRecordStatus.choices,
        default=PayoutRecordStatus.PENDING,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.writer.user.email} | {self.amount} | {self.status}"