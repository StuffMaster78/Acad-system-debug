from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website

from writer_payments_management.enums.financial_event_enums import (
    AdjustmentType,
)


User = settings.AUTH_USER_MODEL


class FinancialAdjustment(models.Model):
    """
    Admin-level correction layer.

    This does NOT directly mutate wallet.

    Instead it:
        • creates adjustment events
        • links to financial event system
        • maintains audit integrity
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="financial_adjustments",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="financial_adjustments",
    )

    adjustment_type = models.CharField(
        max_length=32,
        choices=AdjustmentType.choices,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    reason = models.TextField()

    direction = models.CharField(
        max_length=10,
        choices=[
            ("CREDIT", "Credit"),
            ("DEBIT", "Debit"),
        ],
    )

    related_financial_event = models.ForeignKey(
        "writer_payments_management.FinancialEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adjustments",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_financial_adjustments",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_financial_adjustments",
    )

    is_applied = models.BooleanField(
        default=False,
    )

    applied_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["writer", "adjustment_type"]),
            models.Index(fields=["website", "writer"]),
        ]

    def __str__(self) -> str:
        return f"{self.writer.user.email} | {self.adjustment_type} | {self.amount}"