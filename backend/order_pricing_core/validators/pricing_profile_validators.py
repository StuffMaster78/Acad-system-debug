"""
Pricing profile validators for the order_pricing_core app.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError

from order_pricing_core.models import WebsitePricingProfile


def validate_pricing_profile(
    profile: WebsitePricingProfile,
) -> None:
    """
    Validate website pricing profile values.
    """
    _validate_non_negative(profile)
    _validate_spacing(profile)
    _validate_urgency(profile)


def _validate_non_negative(
    profile: WebsitePricingProfile,
) -> None:
    """
    Ensure profile numeric values are not negative.
    """
    field_names = (
        "base_price_per_page",
        "base_price_per_slide",
        "base_price_per_diagram",
        "double_spacing_multiplier",
        "single_spacing_multiplier",
        "preferred_writer_fee",
        "minimum_paper_order_charge",
        "minimum_design_order_charge",
        "minimum_diagram_order_charge",
    )

    for field_name in field_names:
        value = getattr(profile, field_name)
        if value < 0:
            raise ValidationError(
                {field_name: "Value cannot be negative."}
            )


def _validate_spacing(
    profile: WebsitePricingProfile,
) -> None:
    """
    Validate spacing multiplier assumptions.
    """
    if profile.double_spacing_multiplier <= Decimal("0"):
        raise ValidationError(
            {
                "double_spacing_multiplier": (
                    "Double spacing multiplier must be greater "
                    "than zero."
                )
            }
        )

    if profile.single_spacing_multiplier <= Decimal("0"):
        raise ValidationError(
            {
                "single_spacing_multiplier": (
                    "Single spacing multiplier must be greater "
                    "than zero."
                )
            }
        )


def _validate_urgency(
    profile: WebsitePricingProfile,
) -> None:
    """
    Validate urgent-order recommendation settings.
    """
    if profile.max_pages_per_hour <= 0:
        raise ValidationError(
            {
                "max_pages_per_hour": (
                    "Max pages per hour must be greater than zero."
                )
            }
        )

    if profile.extra_hour_per_extra_page <= 0:
        raise ValidationError(
            {
                "extra_hour_per_extra_page": (
                    "Extra hour per extra page must be greater "
                    "than zero."
                )
            }
        )