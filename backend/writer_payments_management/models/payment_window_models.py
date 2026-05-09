# models/payment_window_models.py

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website

from writer_payments_management.enums.financial_event_enums import (
    PaymentWindowStatus,
)
from writer_payments_management.enums.financial_event_enums import (
    PaymentWindowType,
)


User = settings.AUTH_USER_MODEL


class PaymentWindow(models.Model):
    """
    Configurable writer payment cycle.

    Examples:
        • Monthly
        • Biweekly

    Controls:
        • settlement grouping
        • payout availability
        • advance payment eligibility
        • locking and reconciliation
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_payment_windows",
    )

    title = models.CharField(
        max_length=255,
    )

    window_type = models.CharField(
        max_length=32,
        choices=PaymentWindowType.choices,
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentWindowStatus.choices,
        default=PaymentWindowStatus.UPCOMING,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    payout_date = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_locked = models.BooleanField(
        default=False,
    )

    allow_advances = models.BooleanField(
        default=True,
    )

    advance_percentage_cap = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("30.00"),
        help_text=(
            "Maximum percentage of matured earnings "
            "eligible for advance requests."
        ),
    )

    minimum_advance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("50.00"),
    )

    notes = models.TextField(
        blank=True,
    )

    locked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_writer_payment_windows",
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
            "-start_date",
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
                    "window_type",
                ]
            ),
            models.Index(
                fields=[
                    "start_date",
                    "end_date",
                ]
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.title} "
            f"({self.start_date} → {self.end_date})"
        )

    @property
    def is_open(self) -> bool:
        return (
            self.status == PaymentWindowStatus.OPEN
        )

    @property
    def is_closed(self) -> bool:
        return (
            self.status == PaymentWindowStatus.CLOSED
        )

    @property
    def is_processing(self) -> bool:
        return (
            self.status == PaymentWindowStatus.LOCKED
        )