from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website

from writer_compensation.enums.compensation_enums import (
    WindowStatus,
    WindowType,
)


User = settings.AUTH_USER_MODEL


class PaymentWindow(models.Model):
    """
    Configurable writer compensation cycle.
    A defined pay period.
    Every CompensationEvent belongs to exactly one window.

    Lifecycle (one-way, never reversed):
        UPCOMING -> created ahead of time; not yet accepting events
        OPEN -> events are collected; writers work normally
        CLOSED -> period ended; batch and items created; no new events assigned
        PROCESSING -> admin clicked "Process payments"; writers see status message;
                     all events locked
        DONE -> admin finished; held items remain open indefinitely

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
        on_delete=models.PROTECT,
        related_name="writer_payment_windows",
    )

    title = models.CharField(
        max_length=255,
    )
     # FIX: renamed from window_type to cycle_type for consistency with
    # WriterPayoutPreference.cycle_type and CycleChangeRequest fields.
    cycle_type = models.CharField(
        max_length=32,
        choices=WindowType.choices,
    )

    status = models.CharField(
        max_length=32,
        choices=WindowStatus.choices,
        default=WindowStatus.UPCOMING,
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
    # FIX: renamed from is_locked to avoid property name clash.
    # Use the is_locked @property below for read access.
    # Use locked field only for explicit admin-forced locks outside lifecycle.

    locked = models.BooleanField(
        default=False,
        help_text=(
            "Set to True to hard-lock this window outside normal lifecycle. "
            "Prefer using status transitions (PROCESSING / DONE) instead."
        ),
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
        unique_together = [("website", "start_date", "cycle_type")]
        indexes = [
            models.Index(
                fields=[
                    "website",
                    "status",
                ]
            ),
            models.Index(
                fields=[
                    "cycle_type",
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
            f"({self.start_date} -> {self.end_date})"
            f" [{self.status}]"
        )

     # Status shorthand properties

    @property
    def is_open(self) -> bool:
        return (
            self.status == WindowStatus.OPEN
        )

    @property
    def is_closed(self) -> bool:
        return (
            self.status == WindowStatus.CLOSED
        )

    @property
    def is_processing(self) -> bool:
        return (
            self.status == WindowStatus.PROCESSING
        )
    @property
    def is_done(self) -> bool:
        return self.status == WindowStatus.DONE

    @property
    def is_locked(self) -> bool:
        """
        True when no event changes are allowed.
        Events are locked once window moves to PROCESSING or DONE,
        or when the explicit locked field is set.
        """
        # FIX: was a BooleanField shadowing this property.
        # Now computed from status + explicit lock field.
        return self.locked or self.status in {
            WindowStatus.PROCESSING,
            WindowStatus.DONE,
        }

    @property
    def accepts_events(self) -> bool:
        """True only while the window is OPEN and not explicitly locked."""
        return self.status == WindowStatus.OPEN and not self.locked
