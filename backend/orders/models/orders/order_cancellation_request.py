from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from websites.models.websites import Website


class OrderCancellationRequest(models.Model):
    """
    Represents a client-initiated cancellation request that requires
    staff review before the order is actually cancelled.

    Forfeiture fields are auto-calculated from deadline proximity but
    staff can override them before approving.
    """

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_cancellation_requests",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="order_cancellation_requests",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cancellation_requests_made",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    reason = models.TextField()
    pre_request_status = models.CharField(
        max_length=50,
        help_text="Order status before the request was made — used to revert on rejection.",
    )
    forfeiture_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Percentage of order value forfeited (0–80).",
    )
    forfeiture_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancellation_requests_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True, default="")
    requested_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self) -> str:
        return (
            f"CancellationRequest order={self.order_id} "
            f"[{self.status}] by={self.requested_by_id}"
        )
