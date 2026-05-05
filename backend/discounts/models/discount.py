from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from discounts.constants import DiscountOrigin, DiscountType


class Discount(models.Model):
    """
    Client facing discount code.

    This model stores discount data only. Validation, calculation,
    selection, and application live in services.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discounts",
    )
    campaign = models.ForeignKey(
        "discounts.PromotionalCampaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="discounts",
    )

    discount_code = models.CharField(max_length=64)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    discount_type = models.CharField(
        max_length=32,
        choices=DiscountType.CHOICES,
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
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

    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    per_client_usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    first_order_only = models.BooleanField(default=False)

    eligible_clients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="eligible_discounts",
    )

    origin = models.CharField(
        max_length=32,
        choices=DiscountOrigin.CHOICES,
        default=DiscountOrigin.MANUAL,
    )

    is_campaign_managed = models.BooleanField(
        default=True,
        help_text=(
            "If true, campaign activation/deactivation controls this discount."
        ),
    )
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_discounts",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_discounts",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["website", "discount_code"],
                name="unique_discount_code_per_website",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "discount_code"]),
            models.Index(fields=["website", "origin"]),
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "is_archived"]),
            models.Index(fields=["website", "is_deleted"]),
            models.Index(fields=["starts_at", "ends_at"]),
        ]

    def __str__(self) -> str:
        return self.discount_code