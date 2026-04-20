"""
Pricing profile selectors for the order_pricing_core app.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from order_pricing_core.models import WebsitePricingProfile


def get_active_pricing_profile(*, website) -> WebsitePricingProfile:
    """
    Return the active pricing profile for a website.
    """
    try:
        return WebsitePricingProfile.objects.get(
            website=website,
            is_active=True,
        )
    except WebsitePricingProfile.DoesNotExist as exc:
        raise ValidationError(
            {"website": "Active pricing profile not found."}
        ) from exc


def get_pricing_profile_by_id(
    *,
    website,
    profile_id: int,
) -> WebsitePricingProfile:
    """
    Return a pricing profile by id for a website.
    """
    try:
        return WebsitePricingProfile.objects.get(
            id=profile_id,
            website=website,
        )
    except WebsitePricingProfile.DoesNotExist as exc:
        raise ValidationError(
            {"profile_id": "Pricing profile not found."}
        ) from exc