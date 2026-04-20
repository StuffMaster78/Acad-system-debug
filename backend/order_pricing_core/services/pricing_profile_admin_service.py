"""
Admin service for pricing profile management.
"""

from __future__ import annotations

from django.db import transaction

from order_pricing_core.selectors.pricing_profile_selectors import (
    get_active_pricing_profile,
)
from order_pricing_core.validators.pricing_profile_validators import (
    validate_pricing_profile,
)


class PricingProfileAdminService:
    """
    Admin-facing service for website pricing profile management.
    """

    @classmethod
    @transaction.atomic
    def update_active_profile(
        cls,
        *,
        website,
        data: dict,
    ):
        """
        Update the active pricing profile for a website.
        """
        profile = get_active_pricing_profile(website=website)

        for field, value in data.items():
            setattr(profile, field, value)

        validate_pricing_profile(profile)
        profile.save()

        return profile