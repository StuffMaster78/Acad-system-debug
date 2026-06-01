from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website
from writer_compensation.enums.compensation_enums import (
    PayoutRecordStatus,
)


User = settings.AUTH_USER_MODEL


class PayoutRecord(models.Model):
    """
    Per writer payout instruction inside a batch.
    One writer's payout line within a PayoutBatch.

    This is NOT money movement.
    This is "intent to pay".

     Moves independently of other items in the same batch:
        PENDING -> initial state when batch is created
        CONFIRMED -> admin has reviewed and confirmed this writer's total
        PAID -> admin has paid this writer externally and marked it done
        HELD -> admin has flagged this writer; unblocks when admin resolves
        DEFERRED -> carried to next window (e.g. negative balance)
        FAILED -> payment attempt failed externally

    A window can be marked DONE while some PayoutItems are still HELD.
    HELD items remain open indefinitely until admin resolves them.

    When an item moves to PAID all linked CompensationEvents for this writer
    in this window are stamped PAID by the service layer.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.PROTECT,
        related_name="payout_records",
    )

    batch = models.ForeignKey(
        "writer_compensation.PayoutBatch",
        on_delete=models.CASCADE,
        related_name="records",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.PROTECT,
        related_name="payout_records",
    )

    # FIX: was non-nullable. WindowService.close_window() doesn't have a
    # SettlementPeriod at batch-creation time — settlement runs separately.
    # Made nullable so close_window() can create records without it.
    # Service layer links settlement_period later during settlement pipeline.
    settlement_period = models.ForeignKey(
        "writer_compensation.SettlementPeriod",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="payout_records",
    )

    hold_reason = models.TextField(blank=True)

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    external_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    confirmed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmed_payout_items",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    paid_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="paid_payout_items",
    )

    status = models.CharField(
        max_length=32,
        choices=PayoutRecordStatus.choices,
        default=PayoutRecordStatus.PENDING,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = [("batch", "writer")]
        ordering = ["-batch__created_at", "writer_id"]
        indexes = [
            models.Index(fields=["batch", "status"]),
            models.Index(fields=["writer", "status"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.writer.pk}| {self.writer.user.email} | batch {self.batch.pk}"
            f" | ${self.total_amount} [{self.status}]"
        )