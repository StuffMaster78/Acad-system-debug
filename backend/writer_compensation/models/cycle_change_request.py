from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from writer_compensation.enums.compensation_enums import (
    CycleChangeStatus,
    WindowType,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)
User = settings.AUTH_USER_MODEL




class PaymentWindowChangeRequest(models.Model):
    """
    Writer requests a payout window change. Admin approves or rejects.

    On approval, effective_from_window is set to the next open window
    and WriterPayoutPreference.cycle_window is updated.
    Changes never apply mid-cycle.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.PROTECT,
        related_name="window_change_requests",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.PROTECT,
        related_name="window_change_requests",
    )
    from_window = models.CharField(
        max_length=16,
        choices=WindowType.choices,
    )
    requested_window = models.CharField(
        max_length=16,
        choices=WindowType.choices,
    )
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=CycleChangeStatus.choices,
        default=CycleChangeStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_window_change_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Set on approval — the window where the new cycle first takes effect.
    effective_from_window = models.ForeignKey(
        PaymentWindow,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_window_changes_effective",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["writer", "status"]),
            models.Index(fields=["website", "status"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.writer.pk} | {self.from_window} → {self.requested_window}"
            f" [{self.status}]"
        )