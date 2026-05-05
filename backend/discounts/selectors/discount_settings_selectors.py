from __future__ import annotations

from discounts.exceptions import DiscountConfigurationError
from discounts.models import DiscountSettings


class DiscountSettingsSelector:
    """
    Read helper for tenant discount settings.
    """

    @staticmethod
    def get_or_create_for_website(
        *,
        website,
        user=None,
    ) -> DiscountSettings:
        """
        Return discount settings for a website.

        Creates default settings if they do not exist.
        """
        if not website or not getattr(website, "id", None):
            raise DiscountConfigurationError(
                "A valid website is required."
            )

        defaults = {}

        if user is not None:
            defaults = {
                "created_by": user,
                "updated_by": user,
            }

        settings_obj, _ = DiscountSettings.objects.get_or_create(
            website=website,
            defaults=defaults,
        )

        return settings_obj