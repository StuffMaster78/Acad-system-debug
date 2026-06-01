"""
Canonical order pricing calculator service.

This is the authoritative location for order price calculations.
All views and actions should import from here, not from old_services.
"""
from __future__ import annotations

from decimal import Decimal
from functools import lru_cache
from typing import Any

from django.apps import apps
from django.utils import timezone


class PricingCalculatorService:
    """
    Calculate all pricing components for an order.

    Uses ``order_pricing_core.PricingConfiguration`` for base rates and
    ``discounts.services.discount_calculation_service`` for discount maths.
    """

    def __init__(self, order: Any) -> None:
        self.order = order
        self.website = order.website
        self.config = self.get_pricing_config()

    # ------------------------------------------------------------------
    # Config helpers
    # ------------------------------------------------------------------

    @staticmethod
    @lru_cache(maxsize=64)
    def get_pricing_config_for_website(website_id: int) -> Any:
        PricingConfiguration = apps.get_model("order_pricing_core", "PricingConfiguration")
        config = (
            PricingConfiguration.objects.filter(website_id=website_id)
            .order_by("-created_at")
            .first()
        )
        if config is None:
            raise ValueError(
                f"No PricingConfiguration found for website {website_id}."
            )
        return config

    def get_pricing_config(self) -> Any:
        return self.get_pricing_config_for_website(self.website.id)

    # ------------------------------------------------------------------
    # Component calculators
    # ------------------------------------------------------------------

    def calculate_base_price(self) -> Decimal:
        order = self.order
        config = self.config
        pages = getattr(order, "number_of_pages", 0) or 0
        slides = getattr(order, "number_of_slides", 0) or 0
        price = Decimal(pages) * config.base_price_per_page
        price += Decimal(slides) * config.base_price_per_slide
        return price

    def get_deadline_multiplier(self) -> Decimal:
        """
        Return the multiplier that applies to this order's client_deadline.
        Falls back to 1.0 when no deadline multipliers are configured.

        Queries the DeadlineMultiplier rows attached to PricingConfiguration
        and picks the first window whose max_hours >= hours_remaining.
        """
        deadline = getattr(self.order, "client_deadline", None)
        if deadline is None:
            return Decimal("1.0")

        hours_remaining = max(
            0, (deadline - timezone.now()).total_seconds() / 3600
        )
        try:
            # DeadlineMultiplier has max_hours and multiplier fields.
            dm = (
                self.config.deadline_multipliers
                .filter(max_hours__gte=hours_remaining)
                .order_by("max_hours")
                .first()
            )
            return Decimal(str(dm.multiplier)) if dm is not None else Decimal("1.0")
        except Exception:
            return Decimal("1.0")

    def calculate_discount(self) -> Decimal:
        """
        Return the absolute discount amount for the order.
        """
        from discounts.services.discount_calculation_service import (
            DiscountCalculationService,
        )

        discount = getattr(self.order, "discount", None)
        if discount is None:
            return Decimal("0.00")
        subtotal = self.calculate_base_price() * self.get_deadline_multiplier()
        try:
            return DiscountCalculationService.calculate_amount(
                discount=discount, subtotal=subtotal
            )
        except Exception:
            return Decimal("0.00")

    # ------------------------------------------------------------------
    # Summary methods
    # ------------------------------------------------------------------

    def calculate_total_price(self) -> Decimal:
        base = self.calculate_base_price()
        multiplier = self.get_deadline_multiplier()
        discount = self.calculate_discount()
        preferred_fee = getattr(self.order, "preferred_writer_fee_amount", Decimal("0.00")) or Decimal("0.00")
        total = (base * multiplier) - discount + preferred_fee
        return max(total, Decimal("0.00"))

    def calculate_breakdown(self) -> dict[str, Any]:
        base = self.calculate_base_price()
        multiplier = self.get_deadline_multiplier()
        discount = self.calculate_discount()
        preferred_fee = getattr(self.order, "preferred_writer_fee_amount", Decimal("0.00")) or Decimal("0.00")
        subtotal = base * multiplier
        total = max(subtotal - discount + preferred_fee, Decimal("0.00"))

        return {
            "base_price": float(base),
            "deadline_multiplier": float(multiplier),
            "subtotal": float(subtotal),
            "discount": float(discount),
            "preferred_writer": float(preferred_fee),
            "final_total": float(total),
        }
