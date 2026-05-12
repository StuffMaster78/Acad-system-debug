# models/payment_window_models.py

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website

from writer_compensation.enums.financial_event_enums import (
    PaymentWindowStatus,
)
from writer_compensation.enums.financial_event_enums import (
    PaymentWindowType,
)


User = settings.AUTH_USER_MODEL


class PaymentWindow(models.Model):
    """
    Configurable writer compensation cycle.
    A defined pay period.
    Every CompensationEvent belongs to exactly one window.

    Lifecycle (one-way, never reversed):
        OPEN       -> events are collected; writers work normally
        CLOSED     -> period ended; batch and items created; no new events assigned
        PROCESSING -> admin clicked "Process payments"; writers see status message;
                     all events locked
        DONE       -> admin finished; held items remain open indefinitely

    Examples:
        • Monthly
        • Biweekly

    Controls:
        • settlement grouping
        • payout availability
        • advance compensation eligibility
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
    processing_at = models.DateTimeField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)

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
        unique_together = [("website", "start_date", "window_type")]
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
                    "website",
                    "start_date",
                    "end_date",
                ]
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.website.pk} | {self.title} "
            f"({self.start_date} → {self.end_date})"
            f" [{self.status}]"
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
    
    # @property
    # def is_locked(self) -> bool:
    #     """No event changes once PROCESSING or DONE."""
    #     return self.status in {PaymentWindowStatus.PROCESSING, PaymentWindowStatus.CLOSED}
