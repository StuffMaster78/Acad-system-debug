"""
Pricing profile models for the order_pricing_core app.

These models store website-wide pricing anchors and defaults.
Business rules and validation belong in services and validators.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models


class WebsitePricingProfile(models.Model):
    """
    Stores website-wide pricing anchors for normal order pricing.

    This model is intentionally kept dumb. Validation and business
    rules should live in services and validators.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="orders_pricing_profile",
    )
    profile_name = models.CharField(
        max_length=255,
        default="Default Pricing Profile",
    )
    cloned_from_website = models.ForeignKey(
        "websites.Website",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cloned_orders_pricing_profiles",
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
    )
    base_price_per_page = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    base_price_per_slide = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    base_price_per_diagram = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    double_spacing_multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )
    single_spacing_multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("2.0000"),
    )
    preferred_writer_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    minimum_paper_order_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    minimum_design_order_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    minimum_diagram_order_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    max_pages_per_hour = models.PositiveIntegerField(default=1)
    extra_hour_per_extra_page = models.PositiveIntegerField(default=1)
    rush_recommendation_only = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    allow_customization = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_website_pricing_profile"

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.website} pricing profile"