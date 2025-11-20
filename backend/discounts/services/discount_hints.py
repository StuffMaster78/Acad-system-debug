"""
Service to generate stackable discount hints for users.
"""

import logging
from hashlib import md5

from django.core.cache import cache
from django.utils.timezone import now

from discounts.services.config import DiscountConfigService

logger = logging.getLogger(__name__)


def get_discount_model():
    from discounts.models import Discount
    return Discount


class DiscountHintService:
    """
    Provides stackable discount hints based on applied codes and site config.
    """

    @staticmethod
    def _make_cache_key(current_codes, website_id):
        """
        Generate a unique cache key for a website and current codes.

        Args:
            current_codes (list): List of applied discount codes.
            website_id (int): ID of the website.

        Returns:
            str: Hashed cache key string.
        """
        key = f"{website_id}:{','.join(sorted(current_codes))}"
        hashed = md5(key.encode()).hexdigest()
        return f"discount_hint:{hashed}"

    @staticmethod
    def _valid_now_filters(current_time):
        """
        Returns filters dict for discounts valid at current_time.
        """
        return {
            "valid_from__lte": current_time,
            "valid_until__gte": current_time,
            "is_active": True
        }

    @classmethod
    def get_stackable_hint(cls, current_codes, website):
        """
        Return a stackable hint message if applicable.

        Args:
            current_codes (list): List of applied discount codes.
            website (Website): The website instance to fetch configuration.

        Returns:
            dict or None: Suggested discount hint or None if no hint.
        """
        cache_key = cls._make_cache_key(current_codes, website.id)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        config = DiscountConfigService.get_config(website)
        if not (config.get("ENABLE_HINTS") and config.get("ENABLE_STACKING")):
            cache.set(cache_key, None, timeout=60)  # Cache negative result briefly
            return None

        if len(current_codes) >= 2:
            cache.set(cache_key, None, timeout=60)  # Cache negative result briefly
            return None

        current_time = now()
        Discount = get_discount_model()

        try:
            valid_discounts = Discount.objects.filter(
                code__in=current_codes,
                website=website,
                is_active=True
            )
        except Exception as e:
            logger.error("Error fetching valid discounts: %s", e)
            return None

        if not valid_discounts.exists():
            logger.info(
                "No active discounts found for codes: %s on website %s",
                current_codes, website.id
            )
            cache.set(cache_key, None, timeout=60)
            return None

        if not all(d.stackable for d in valid_discounts):
            cache.set(cache_key, None, timeout=60)
            return None

        try:
            potential_discounts = Discount.objects.filter(
                website=website,
                stackable=True,
                **cls._valid_now_filters(current_time)
            ).exclude(code__in=current_codes)
        except Exception as e:
            logger.error("Error fetching potential stackable discounts: %s", e)
            return None

        for discount in potential_discounts:
            result = {
                "hint": (
                    f"You can stack this code: {discount.code} "
                    "for more savings!"
                ),
                "suggested_code": discount.code
            }
            cache.set(cache_key, result, timeout=180)
            return result

        cache.set(cache_key, None, timeout=60)
        return None