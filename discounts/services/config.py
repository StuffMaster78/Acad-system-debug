"""
Service to retrieve and manage discount configuration settings per website,
with simple in-memory caching for performance.
"""

import logging
import time
from discounts.models.discount_configs import DiscountConfig

logger = logging.getLogger(__name__)

DEFAULT_DISCOUNT_CONFIG = {
    "ENABLE_STACKING": True,
    "MAX_STACKABLE_DISCOUNTS": 1,
    "ENABLE_HINTS": True,
    "DISCOUNT_THRESHOLD": 100.00,
    "MAX_DISCOUNT_PERCENT": 20.00,
    "ALLOW_STACK_ACROSS_EVENTS": False,
    "SEASONAL_DISCOUNT_ACTIVE": True,
    "SEASONAL_DISCOUNT_VALUE": 10.00,
    "SEASONAL_EVENT_ID": None,
}

_CACHE = {}
_CACHE_TTL = 300  # seconds


class DiscountConfigService:
    """
    Fetches effective discount configuration for a given website,
    merging DB config and default fallback values.

    Uses in-memory cache with TTL for better performance.
    """

    @staticmethod
    def get_config(website):
        """
        Retrieve merged discount config for a website, caching results.

        Args:
            website (Website): Website instance to get config for

        Returns:
            dict: Merged discount configuration values
        """
        cache_key = website.id
        now = time.time()

        # Check cache
        if cache_key in _CACHE:
            cached_value, timestamp = _CACHE[cache_key]
            if now - timestamp < _CACHE_TTL:
                return cached_value

        # Cache miss or expired, load from DB
        try:
            db_config = website.discount_config
        except DiscountConfig.DoesNotExist:
            logger.warning(
                f"No DiscountConfig found for website {website.id}. Using default."
            )
            config = DEFAULT_DISCOUNT_CONFIG.copy()
        else:
            config = {
                "ENABLE_STACKING": db_config.enable_stacking,
                "MAX_STACKABLE_DISCOUNTS": db_config.max_stackable_discounts,
                "ENABLE_HINTS": db_config.enable_hints,
                "DISCOUNT_THRESHOLD": float(db_config.discount_threshold),
                "MAX_DISCOUNT_PERCENT": float(db_config.max_discount_percent),
                "ALLOW_STACK_ACROSS_EVENTS": db_config.allow_stack_across_events,
                "SEASONAL_DISCOUNT_ACTIVE": db_config.seasonal_discount_active,
                "SEASONAL_DISCOUNT_VALUE": float(db_config.seasonal_discount_value),
                "SEASONAL_EVENT_ID": db_config.seasonal_event_id,
            }

        _CACHE[cache_key] = (config, now)
        return config
