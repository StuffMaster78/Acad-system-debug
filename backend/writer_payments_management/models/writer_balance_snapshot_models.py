from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website


User = settings.AUTH_USER_MODEL


class WriterBalanceSnapshot(models.Model):
    """
    Frozen snapshot of writer financial state
    at a specific point in time.

    This is NOT used for calculations.

    It is used for:
        • audits
        • reconciliation
        • dispute investigation
        • payout verification
        • system rollback analysis
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_balance_snapshots",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="balance_snapshots",
    )

    payment_window = models.ForeignKey(
        "writer_payments_management.PaymentWindow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="balance_snapshots",
    )

    wallet_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    gross_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    net_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_advances = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_pending = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    captured_at = models.DateTimeField(
        auto_now_add=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["writer", "captured_at"]),
            models.Index(fields=["website", "writer"]),
        ]

    def __str__(self) -> str:
        return f"{self.writer.user.email} | {self.wallet_balance} @ {self.captured_at}"