from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    DiscountScope,
    DiscountStatus,
    DiscountType,
)


class SpecialOrderDiscountRule(TimeStampedModel):
    """
    Tenant-scoped discount rule for special orders.

    This can power coupon codes, seasonal discounts, repeat-client
    incentives, or admin-created promotional rules.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_discount_rules",
    )

    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Optional coupon code used by clients.",
    )

    discount_type = models.CharField(
        max_length=50,
        choices=DiscountType.CHOICES,
    )
    scope = models.CharField(
        max_length=50,
        choices=DiscountScope.CHOICES,
        default=DiscountScope.ALL_SPECIAL_ORDERS,
    )
    status = models.CharField(
        max_length=50,
        choices=DiscountStatus.CHOICES,
        default=DiscountStatus.ACTIVE,
    )

    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=(
            "Percentage value for percentage discounts, or money amount "
            "for fixed discounts."
        ),
    )
    max_discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    minimum_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)

    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    is_stackable = models.BooleanField(
        default=False,
        help_text="Whether this discount can combine with other discounts.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_special_order_discount_rules",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["website", "code"],
                name="unique_special_order_discount_code_per_site",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "code"]),
            models.Index(fields=["website", "scope"]),
            models.Index(fields=["website", "expires_at"]),
        ]

    def __str__(self) -> str:
        return self.name

    if TYPE_CHECKING:
        id: int
        website_id: int


class SpecialOrderDiscountApplication(TimeStampedModel):
    """
    Auditable discount applied to a quote or special order.

    Discounts should be applied before the funding plan is locked.
    After payment has started, use adjustment or refund flows instead.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_discount_applications",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="discount_applications",
    )
    quote = models.ForeignKey(
        "special_orders.SpecialOrderQuote",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="discount_applications",
    )
    discount_rule = models.ForeignKey(
        "special_orders.SpecialOrderDiscountRule",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applications",
    )

    discount_type = models.CharField(
        max_length=50,
        choices=DiscountType.CHOICES,
    )
    status = models.CharField(
        max_length=50,
        choices=DiscountStatus.CHOICES,
        default=DiscountStatus.USED,
    )

    code = models.CharField(max_length=100, null=True, blank=True)
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    amount_applied = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    reason = models.TextField(blank=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_special_order_discounts",
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applied_special_order_discounts",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "quote"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "code"]),
        ]

    def __str__(self) -> str:
        return (
            f"DiscountApplication("
            f"order={self.special_order_id}, "
            f"amount={self.amount_applied})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int
        quote_id: int | None
        discount_rule_id: int | None