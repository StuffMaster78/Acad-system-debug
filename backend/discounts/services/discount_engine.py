"""
Compat stub — DiscountEngine was removed.
Tests referencing DiscountEngine need to be updated to use
discounts.services.discount_application_service.DiscountApplicationService.
"""
from decimal import Decimal


class DiscountEngine:
    """Stub class — raises NotImplementedError to surface stale test failures."""

    @staticmethod
    def apply_discount_to_order(order, discount_code, **kwargs):
        raise NotImplementedError(
            "DiscountEngine removed — use DiscountApplicationService instead."
        )

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "DiscountEngine removed — use DiscountApplicationService instead."
        )
