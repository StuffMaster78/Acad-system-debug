"""
Compatibility tracker for legacy discount usage callers.
"""

from discounts.services.discount_usage_service import DiscountUsageService


class DiscountUsageTracker:
    @staticmethod
    def track(*args, **kwargs):
        return DiscountUsageService.create_usage(*args, **kwargs)

    @staticmethod
    def untrack(*args, **kwargs):
        return None
