from __future__ import annotations

from special_orders.constants import SpecialOrderPricingMode


class SpecialOrderValidator:
    """
    Validates SpecialOrder creation/update constraints.
    """

    @staticmethod
    def validate_pricing_mode_consistency(*, pricing_mode, config):
        if pricing_mode == SpecialOrderPricingMode.FIXED_CONFIG and not config:
            raise ValueError("Fixed pricing requires a predefined config.")

        if pricing_mode == SpecialOrderPricingMode.QUOTED and config:
            raise ValueError("Quoted pricing should not have predefined config.")