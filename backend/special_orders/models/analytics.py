from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from django.conf import settings

from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    SpecialOrderAnalyticsEventType,
    SpecialOrderConversionStage,
)


class SpecialOrderAnalyticsEvent(TimeStampedModel):
    """
    Append-only analytics event for special order funnel tracking.

    This model should not drive business logic. It exists for reporting,
    dashboards, conversion analysis, and operational insight.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_analytics_events",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="analytics_events",
    )

    event_type = models.CharField(
        max_length=80,
        choices=SpecialOrderAnalyticsEventType.CHOICES,
    )
    conversion_stage = models.CharField(
        max_length=80,
        choices=SpecialOrderConversionStage.CHOICES,
        null=True,
        blank=True,
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="special_order_analytics_events",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=10, default="USD")

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "event_type"]),
            models.Index(fields=["website", "conversion_stage"]),
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"SpecialOrderAnalyticsEvent("
            f"event={self.event_type}, "
            f"order={self.special_order_id})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int | None