"""
Service to retrieve and manage discount configuration settings for a website.
"""

import logging
from discounts.models.discount_configs import DiscountConfig

logger = logging.getLogger(__name__)

# Define fallback defaults (if not already defined globally)
DISCOUNT_CONFIG = {
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


class DiscountConfigService:
    """
    Fetches effective discount configuration for a given website,
    merging DB and default settings.
    """

    @staticmethod
    def get_config(website):
        """
        Return merged config: DB + fallback defaults.

        Args:
            website: Website instance

        Returns:
            dict with config keys and effective values
        """
        try:
            db_config = website.discount_config
        except DiscountConfig.DoesNotExist:
            logger.warning(f"No DiscountConfig found for website {website.id}. "
                           "Falling back to defaults.")
            return DISCOUNT_CONFIG.copy()  # Safe copy to avoid mutation

        # Construct merged config using DB values
        return {
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
