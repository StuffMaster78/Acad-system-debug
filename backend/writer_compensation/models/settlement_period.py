from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website

from writer_management.models.writer_profile import (
    WriterProfile,
)

from writer_compensation.enums.compensation_enums import (
    SettlementStatus,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)


User = settings.AUTH_USER_MODEL


class SettlementPeriod(models.Model):
    """
    Frozen financial snapshot for a writer
    within a compensation window.

    Stores:
        • matured earnings
        • deductions
        • bonuses
        • advances
        • deferred totals
        • final net payable amount

    SettlementPeriod is the source of truth
    for payout computation.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_settlement_periods",
    )

    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="settlement_periods",
    )

    payment_window = models.ForeignKey(
        PaymentWindow,
        on_delete=models.CASCADE,
        related_name="settlements",
    )

    status = models.CharField(
        max_length=32,
        choices=SettlementStatus.choices,
        default=SettlementStatus.OPEN,
    )

    gross_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_tips = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_bonuses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_adjustments = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_fines = models.DecimalField(
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

    total_deferred = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_reversals = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    net_payable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_financial_events = models.PositiveIntegerField(
        default=0,
    )

    total_settlement_items = models.PositiveIntegerField(
        default=0,
    )

    is_locked = models.BooleanField(
        default=False,
    )

    locked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_writer_settlements",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        unique_together = [
            (
                "writer",
                "payment_window",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "website",
                    "status",
                ]
            ),
            models.Index(
                fields=[
                    "writer",
                    "payment_window",
                ]
            ),
            models.Index(
                fields=[
                    "payment_window",
                    "status",
                ]
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.writer.user.email} | "
            f"{self.payment_window.title}"
        )

    @property
    def remaining_payable_balance(self) -> Decimal:
        return (
            self.net_payable
            - self.total_advances
        )

    @property
    def has_negative_balance(self) -> bool:
        return (
            self.net_payable
            < Decimal("0.00")
        )

    @property
    def can_be_paid_out(self) -> bool:
        return (
            self.status == SettlementStatus.COMPLETED
            and not self.has_negative_balance
        )
