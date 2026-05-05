from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from discounts.constants import PayableType


class DiscountUsage(models.Model):
    """
    Immutable record of a discount consumed by a client.

    This is the financial and support audit trail. Do not mutate old
    usage rows when a discount changes later.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discount_usages",
    )
    discount = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.PROTECT,
        related_name="usages",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="discount_usages",
    )

    payable_type = models.CharField(
        max_length=40,
        choices=PayableType.CHOICES,
    )
    payable_id = models.CharField(max_length=64)

    discount_code = models.CharField(max_length=64)
    discount_type = models.CharField(max_length=32)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

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

    origin = models.CharField(max_length=32)
    metadata = models.JSONField(default=dict, blank=True)

    applied_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-applied_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["website", "payable_type", "payable_id"],
                name="unique_discount_usage_per_payable",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "client"]),
            models.Index(fields=["website", "discount"]),
            models.Index(fields=["website", "payable_type", "payable_id"]),
            models.Index(fields=["website", "origin"]),
            models.Index(fields=["applied_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.discount_code} for {self.payable_type}:{self.payable_id}"