# models/advance_payment_models.py

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website

from writer_compensation.enums.compensation_enums import (
    AdvancePaymentStatus,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)


User = settings.AUTH_USER_MODEL


class AdvancePaymentRequest(models.Model):
    """
    Writer-requested advance
    against matured settlement earnings.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_advance_requests",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="advance_requests",
    )

    payment_window = models.ForeignKey(
        PaymentWindow,
        on_delete=models.CASCADE,
        related_name="advance_requests",
    )

    status = models.CharField(
        max_length=64,
        choices=AdvancePaymentStatus.choices,
        default=AdvancePaymentStatus.PENDING,
    )

    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    recovered_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    reason = models.TextField(
        blank=True,
    )

    admin_notes = models.TextField(
        blank=True,
    )

    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_writer_advances",
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_writer_advances",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
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

    def __str__(self) -> str:
        return (
            f"{self.writer.user.email} | "
            f"{self.requested_amount}"
        )

    @property
    def outstanding_balance(self) -> Decimal:
        return (
            self.approved_amount
            - self.recovered_amount
        )


class AdvanceRecovery(models.Model):
    """
    Tracks automatic or manual
    recovery of advances.
    """

    advance_request = models.ForeignKey(
        AdvancePaymentRequest,
        on_delete=models.CASCADE,
        related_name="recoveries",
    )

    settlement_period = models.ForeignKey(
        "writer_compensation.SettlementPeriod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advance_recoveries",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    recovered_at = models.DateTimeField(
        auto_now_add=True,
    )

    notes = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    def __str__(self) -> str:
        return (
            f"{self.advance_request.pk} | "
            f"{self.amount}"
        )