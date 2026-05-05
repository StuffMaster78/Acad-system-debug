from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from discounts.constants import DiscountType


class FirstOrderDiscountConfig(models.Model):
    """
    Tenant level configuration for automatic first order discounts.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="first_order_discount_config",
    )

    is_enabled = models.BooleanField(default=True)

    discount_type = models.CharField(
        max_length=32,
        choices=DiscountType.CHOICES,
        default=DiscountType.PERCENTAGE,
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    min_payable_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    applies_to_orders = models.BooleanField(default=True)
    applies_to_special_orders = models.BooleanField(default=True)
    applies_to_class_bundles = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_first_order_discount_configs",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_first_order_discount_configs",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "is_enabled"]),
        ]

    def __str__(self) -> str:
        return f"First order discount for {self.website.id}"