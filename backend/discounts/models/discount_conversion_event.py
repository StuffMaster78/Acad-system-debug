from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from discounts.constants import DiscountConversionEvent
from discounts.constants import PayableType


class DiscountConversionEventLog(models.Model):
    """
    Funnel event for discount visibility and conversion tracking.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discount_conversion_events",
    )
    discount = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversion_events",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="discount_conversion_events",
    )

    event = models.CharField(
        max_length=40,
        choices=DiscountConversionEvent.CHOICES,
    )

    payable_type = models.CharField(
        max_length=40,
        choices=PayableType.CHOICES,
        blank=True,
    )
    payable_id = models.CharField(max_length=64, blank=True)

    discount_code = models.CharField(max_length=64, blank=True)

    subtotal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    reason = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "event"]),
            models.Index(fields=["website", "discount"]),
            models.Index(fields=["website", "client"]),
            models.Index(fields=["website", "discount_code"]),
            models.Index(fields=["website", "payable_type", "payable_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event}: {self.discount_code}"