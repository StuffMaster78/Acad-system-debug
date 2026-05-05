from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    DisputeResolutionType,
    DisputeStatus,
)


class SpecialOrderDispute(TimeStampedModel):
    """
    Client or staff dispute against a special order.

    This model only tracks the dispute lifecycle. Refunds, wallet credits,
    or ledger reversals must be handled through dedicated services.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_disputes",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="disputes",
    )

    status = models.CharField(
        max_length=50,
        choices=DisputeStatus.CHOICES,
        default=DisputeStatus.OPEN,
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="opened_special_order_disputes",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_special_order_disputes",
    )

    opened_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"SpecialOrderDispute("
            f"order={self.special_order_id}, "
            f"status={self.status})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderDisputeResolution(TimeStampedModel):
    """
    Final or interim resolution for a special order dispute.

    If the resolution involves money, services must create refund,
    wallet-credit, or ledger reversal records separately.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_dispute_resolutions",
    )
    dispute = models.ForeignKey(
        "special_orders.SpecialOrderDispute",
        on_delete=models.CASCADE,
        related_name="resolutions",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="dispute_resolutions",
    )

    resolution_type = models.CharField(
        max_length=50,
        choices=DisputeResolutionType.CHOICES,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Optional amount for refund or adjustment resolutions.",
    )
    currency = models.CharField(max_length=10, default="USD")

    notes = models.TextField(blank=True)

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_special_order_disputes",
    )

    refund_application = models.ForeignKey(
        "special_orders.SpecialOrderRefundApplication",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dispute_resolutions",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "dispute"]),
            models.Index(fields=["website", "resolution_type"]),
        ]

    def __str__(self) -> str:
        return (
            f"SpecialOrderDisputeResolution("
            f"dispute={self.dispute_id}, "
            f"type={self.resolution_type})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        dispute_id: int
        special_order_id: int
        refund_application_id: int | None