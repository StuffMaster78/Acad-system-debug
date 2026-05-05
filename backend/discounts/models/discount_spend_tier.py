from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class DiscountSpendTier(models.Model):
    """
    Spend based discount tier linked to one reusable discount code.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discount_spend_tiers",
    )
    discount = models.OneToOneField(
        "discounts.Discount",
        on_delete=models.CASCADE,
        related_name="spend_tier",
    )

    name = models.CharField(max_length=120)
    minimum_lifetime_spend = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_discount_spend_tiers",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_discount_spend_tiers",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-minimum_lifetime_spend",)
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "minimum_lifetime_spend"]),
        ]

    def __str__(self) -> str:
        return self.name