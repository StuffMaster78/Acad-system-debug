from __future__ import annotations

from decimal import Decimal
from typing import Any


class WriterScopePricingService:
    """
    Compute writer-facing pricing for pool-order bids and scope
    increment requests.

    All amounts are in the order's currency (USD by default).
    Returns Decimal("0.00") whenever the inputs are insufficient
    rather than raising — callers treat zero as "not computed".
    """

    # ------------------------------------------------------------------ #
    # Bid price suggestion                                                  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def suggested_bid_price(*, writer: Any, order: Any) -> Decimal:
        """
        Compute the writer's level-based price for taking this order.

        Only meaningful when earning_mode == fixed_per_page.
        Percentage-mode writers must enter the price manually (returns 0).
        """
        settings = WriterScopePricingService._get_level_settings(writer)
        if settings is None:
            return Decimal("0.00")

        qty = int(getattr(order, "base_quantity", 0) or 0)
        unit_type = getattr(order, "unit_type", "page") or "page"

        base = WriterScopePricingService._base_rate(settings, unit_type)
        if base <= 0 or qty <= 0:
            return Decimal("0.00")

        price = base * qty

        if getattr(order, "is_urgent", False):
            surcharge = Decimal(str(getattr(settings, "urgent_order_surcharge", "0.00") or "0.00"))
            multiplier = Decimal(str(getattr(settings, "urgent_multiplier", "1.00") or "1.00"))
            price = price * multiplier + surcharge * qty

        return price.quantize(Decimal("0.01"))

    @staticmethod
    def rate_breakdown(*, writer: Any) -> dict:
        """
        Return the writer's per-unit rates for display in the bid form.
        """
        settings = WriterScopePricingService._get_level_settings(writer)
        if settings is None:
            return {}

        return {
            "per_page": str(getattr(settings, "base_pay_per_page", "0.00") or "0.00"),
            "per_slide": str(getattr(settings, "base_pay_per_slide", "0.00") or "0.00"),
            "per_chart": str(getattr(settings, "base_pay_per_chart", "0.00") or "0.00"),
            "urgent_surcharge": str(getattr(settings, "urgent_order_surcharge", "0.00") or "0.00"),
            "urgent_multiplier": str(getattr(settings, "urgent_multiplier", "1.00") or "1.00"),
            "earning_mode": getattr(settings, "earning_mode", "fixed_per_page"),
        }

    # ------------------------------------------------------------------ #
    # Scope increment pricing                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def scope_increment_pricing(
        *,
        writer: Any,
        order: Any,
        quantity_delta: int,
        unit_type: str,
    ) -> dict:
        """
        Compute client price and writer compensation for a scope delta.

        Client price  = current per-unit rate × delta
                        (derived from order.total_price / order.base_quantity)
        Writer comp   = additional_*_pay × delta

        Returns {"total_price": str, "writer_compensation_amount": str}.
        """
        settings = WriterScopePricingService._get_level_settings(writer)

        # Writer compensation delta
        writer_comp = Decimal("0.00")
        if settings is not None and quantity_delta > 0:
            add_rate = WriterScopePricingService._additional_rate(settings, unit_type)
            writer_comp = (add_rate * quantity_delta).quantize(Decimal("0.01"))

        # Client price delta — proportional to current order pricing
        client_price = Decimal("0.00")
        base_qty = int(getattr(order, "base_quantity", 0) or 0)
        total_price = Decimal(str(getattr(order, "total_price", "0.00") or "0.00"))
        if base_qty > 0 and total_price > 0 and quantity_delta > 0:
            per_unit = (total_price / base_qty).quantize(Decimal("0.01"))
            client_price = (per_unit * quantity_delta).quantize(Decimal("0.01"))

        return {
            "total_price": str(client_price),
            "writer_compensation_amount": str(writer_comp),
        }

    # ------------------------------------------------------------------ #
    # Internals                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_level_settings(writer: Any):
        try:
            profile = getattr(writer, "writerprofile", None) or writer
            level = getattr(profile, "writer_level", None)
            if level is None:
                return None
            return getattr(level, "settings", None)
        except Exception:
            return None

    @staticmethod
    def _base_rate(settings: Any, unit_type: str) -> Decimal:
        field_map = {
            "page": "base_pay_per_page",
            "slide": "base_pay_per_slide",
            "chart": "base_pay_per_chart",
            "diagram": "base_pay_per_chart",
            "design_concept": "base_pay_per_page",
            "section": "base_pay_per_page",
        }
        field = field_map.get(unit_type, "base_pay_per_page")
        return Decimal(str(getattr(settings, field, "0.00") or "0.00"))

    @staticmethod
    def _additional_rate(settings: Any, unit_type: str) -> Decimal:
        field_map = {
            "page": "additional_page_pay",
            "slide": "additional_slide_pay",
            "chart": "additional_chart_pay",
            "diagram": "additional_chart_pay",
            "design_concept": "additional_page_pay",
            "section": "additional_page_pay",
        }
        field = field_map.get(unit_type, "additional_page_pay")
        return Decimal(str(getattr(settings, field, "0.00") or "0.00"))
