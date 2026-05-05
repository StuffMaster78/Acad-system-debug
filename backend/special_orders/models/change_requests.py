from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    ChangeRequestPricingImpact,
    ChangeRequestStatus,
)


class SpecialOrderChangeRequest(TimeStampedModel):
    """
    Tracks requested scope changes after a special order is created.

    This prevents unpaid scope creep by requiring staff review and,
    when needed, an additional quote/funding milestone.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_change_requests",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="change_requests",
    )

    status = models.CharField(
        max_length=50,
        choices=ChangeRequestStatus.CHOICES,
        default=ChangeRequestStatus.PENDING,
    )
    pricing_impact = models.CharField(
        max_length=50,
        choices=ChangeRequestPricingImpact.CHOICES,
        default=ChangeRequestPricingImpact.ADDITIONAL_CHARGE,
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_special_order_changes",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_special_order_changes",
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    decision_reason = models.TextField(blank=True)

    estimated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Optional staff estimate before final quote.",
    )
    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Final approved amount for this change request.",
    )

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
            f"ChangeRequest("
            f"order={self.special_order_id}, "
            f"status={self.status})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderChangeRequestQuote(TimeStampedModel):
    """
    Quote created specifically for a change request.

    If accepted, this should create a new funding milestone instead of
    changing the original pricing snapshot.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_change_request_quotes",
    )
    change_request = models.OneToOneField(
        "special_orders.SpecialOrderChangeRequest",
        on_delete=models.CASCADE,
        related_name="quote",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=10, default="USD")

    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_special_order_change_quotes",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "change_request"]),
            models.Index(fields=["website", "expires_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"ChangeRequestQuote("
            f"change_request={self.change_request_id}, "
            f"amount={self.amount})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        change_request_id: int