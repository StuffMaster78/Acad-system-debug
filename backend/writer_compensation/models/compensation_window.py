from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from writer_compensation.enums.compensation_enums import (
    WindowType,
    WindowStatus,
)

User = settings.AUTH_USER_MODEL


# ---------------------------------------------------------------------------
# CompensationWindow
# ---------------------------------------------------------------------------

class CompensationWindow(models.Model):
    """
    A defined pay period. Every CompensationEvent belongs to exactly one window.

    Lifecycle (one-way, never reversed):
        OPEN -> events are collected; writers work normally
        CLOSED -> period ended; batch and items created; no new events assigned
        PROCESSING -> admin clicked "Process payments"; writers see status message;
                     all events locked
        DONE -> admin finished; held items remain open indefinitely
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.PROTECT,
        related_name="compensation_windows",
    )
    cycle_type = models.CharField(
        max_length=16,
        choices=WindowType.choices,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=16,
        choices=WindowStatus.choices,
        default=WindowStatus.OPEN,
    )

    # Transition timestamps — set once, never cleared.
    closed_at = models.DateTimeField(null=True, blank=True)
    processing_at = models.DateTimeField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_compensation_windows",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        unique_together = [("website", "start_date", "cycle_type")]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "start_date", "end_date"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.website.pk} | {self.start_date} - {self.end_date}"
            f" [{self.status}]"
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        return self.status == WindowStatus.OPEN

    @property
    def is_editable(self) -> bool:
        """Events can be added/edited only while the window is OPEN."""
        return self.status == WindowStatus.OPEN

    @property
    def is_locked(self) -> bool:
        """No event changes once PROCESSING or DONE."""
        return self.status in {WindowStatus.PROCESSING, WindowStatus.DONE}

