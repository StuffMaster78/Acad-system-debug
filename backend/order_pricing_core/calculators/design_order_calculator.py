"""
Design order calculator for the order_pricing_core app.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.core.exceptions import ValidationError

from order_pricing_core.calculators.base import BasePricingCalculator
from order_pricing_core.calculators.base import PriceBreakdownItem
from order_pricing_core.calculators.base import PriceCalculationResult
from order_pricing_core.constants import BreakdownLineType
from order_pricing_core.constants import PricingUnit
from order_pricing_core.constants import QuoteMode
from order_pricing_core.models import DeadlineRate
from order_pricing_core.models import ServiceAddon
from order_pricing_core.models import WebsitePricingProfile
from order_pricing_core.validators.quote_input_validators import (
    optional_positive_int,
)
from order_pricing_core.validators.quote_input_validators import (
    require_positive_int,
)

TWOPLACES = Decimal("0.01")


class DesignOrderPricingCalculator(BasePricingCalculator):
    """
    Calculator for standardized design-order services.
    """

    def calculate(
        self,
        *,
        website,
        service,
        payload: dict[str, Any],
        mode: str,
    ) -> PriceCalculationResult:
        """
        Calculate a price result for a design-order service.
        """
        if mode not in {QuoteMode.ESTIMATE, QuoteMode.FINAL}:
            raise ValidationError({"mode": "Unsupported quote mode."})

        profile = WebsitePricingProfile.objects.get(
            website=website,
            is_active=True,
        )

        quantity = self._get_quantity(service=service, payload=payload)
        deadline_hours = optional_positive_int(payload, "deadline_hours")
        addon_codes = payload.get("selected_addon_codes", [])

        if mode == QuoteMode.ESTIMATE:
            return self._estimate_result(
                profile=profile,
                service=service,
                quantity=quantity,
                deadline_hours=deadline_hours,
            )

        return self._final_result(
            website=website,
            profile=profile,
            service=service,
            quantity=quantity,
            deadline_hours=deadline_hours,
            addon_codes=addon_codes,
        )

    def _estimate_result(
        self,
        *,
        profile: WebsitePricingProfile,
        service,
        quantity: int,
        deadline_hours: int | None,
    ) -> PriceCalculationResult:
        """
        Build an estimate-mode result for design work.
        """
        base_amount = self._base_amount_for_service(
            profile=profile,
            service=service,
            quantity=quantity,
        )
        min_total = self._money(
            max(base_amount, profile.minimum_design_order_charge)
        )

        max_multiplier = Decimal("1.3000")
        if deadline_hours is not None and deadline_hours <= 24:
            max_multiplier = Decimal("1.5000")

        max_total = self._money(
            max(
                self._money(base_amount * max_multiplier),
                profile.minimum_design_order_charge,
            )
        )

        lines = [
            PriceBreakdownItem(
                line_type=BreakdownLineType.BASE,
                code="estimate_range",
                label="Estimated price range",
                amount=min_total,
                metadata={"max_total": str(max_total)},
            ),
        ]

        return PriceCalculationResult(
            subtotal=min_total,
            discount_amount=Decimal("0.00"),
            total=min_total,
            lines=lines,
            metadata={
                "estimated_min_price": str(min_total),
                "estimated_max_price": str(max_total),
                "quantity": quantity,
                "pricing_unit": service.pricing_unit,
            },
            suggestions=[],
        )

    def _final_result(
        self,
        *,
        website,
        profile: WebsitePricingProfile,
        service,
        quantity: int,
        deadline_hours: int | None,
        addon_codes: list[Any],
    ) -> PriceCalculationResult:
        """
        Build the final calculated design-order result.
        """
        lines: list[PriceBreakdownItem] = []

        base_amount = self._base_amount_for_service(
            profile=profile,
            service=service,
            quantity=quantity,
        )

        lines.append(
            PriceBreakdownItem(
                line_type=BreakdownLineType.BASE,
                code="design_base",
                label=self._base_label(service=service, quantity=quantity),
                amount=base_amount,
                metadata={
                    "quantity": quantity,
                    "pricing_unit": service.pricing_unit,
                },
            )
        )

        subtotal = base_amount

        if deadline_hours is not None:
            subtotal = self._apply_deadline_rate(
                website=website,
                subtotal=subtotal,
                deadline_hours=deadline_hours,
                lines=lines,
            )

        subtotal = self._apply_addons(
            website=website,
            subtotal=subtotal,
            addon_codes=addon_codes,
            lines=lines,
        )

        subtotal = self._money(
            max(subtotal, profile.minimum_design_order_charge)
        )

        if subtotal < service.minimum_charge:
            subtotal = self._money(service.minimum_charge)

        discount_amount = Decimal("0.00")
        total = self._money(subtotal - discount_amount)

        lines.append(
            PriceBreakdownItem(
                line_type=BreakdownLineType.TOTAL,
                code="total",
                label="Total",
                amount=total,
            )
        )

        return PriceCalculationResult(
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total,
            lines=lines,
            metadata={
                "quantity": quantity,
                "deadline_hours": deadline_hours,
                "addon_codes": addon_codes,
                "pricing_unit": service.pricing_unit,
                "service_code": service.service_code,
            },
            suggestions=[],
        )

    def _get_quantity(self, *, service, payload: dict[str, Any]) -> int:
        """
        Resolve quantity based on the service pricing unit.
        """
        if service.pricing_unit == PricingUnit.SLIDE:
            return require_positive_int(payload, "slides", "Slides")

        if service.pricing_unit == PricingUnit.QUANTITY:
            return require_positive_int(payload, "quantity", "Quantity")

        if service.pricing_unit == PricingUnit.ITEM:
            value = optional_positive_int(payload, "quantity")
            return value if value is not None else 1

        if service.pricing_unit == PricingUnit.ORDER:
            return 1

        raise ValidationError(
            {"pricing_unit": "Unsupported design pricing unit."}
        )

    def _base_amount_for_service(
        self,
        *,
        profile: WebsitePricingProfile,
        service,
        quantity: int,
    ) -> Decimal:
        """
        Return the base amount for the design service.
        """
        if service.pricing_unit == PricingUnit.SLIDE:
            slide_total = Decimal(quantity) * profile.base_price_per_slide
            if service.base_amount > Decimal("0.00"):
                slide_total = Decimal(quantity) * service.base_amount
            return self._money(slide_total)

        if service.pricing_unit == PricingUnit.QUANTITY:
            unit_amount = service.base_amount
            return self._money(Decimal(quantity) * unit_amount)

        if service.pricing_unit == PricingUnit.ITEM:
            unit_amount = service.base_amount
            return self._money(Decimal(quantity) * unit_amount)

        if service.pricing_unit == PricingUnit.ORDER:
            return self._money(service.base_amount)

        raise ValidationError(
            {"pricing_unit": "Unsupported design pricing unit."}
        )

    def _base_label(self, *, service, quantity: int) -> str:
        """
        Return a readable base line label.
        """
        if service.pricing_unit == PricingUnit.SLIDE:
            return f"Base price for {quantity} slides"

        if service.pricing_unit == PricingUnit.QUANTITY:
            return f"Base price for {quantity} items"

        if service.pricing_unit == PricingUnit.ITEM:
            if quantity == 1:
                return "Base price for design item"
            return f"Base price for {quantity} design items"

        if service.pricing_unit == PricingUnit.ORDER:
            return "Base price for order"

        return "Base price"

    def _apply_deadline_rate(
        self,
        *,
        website,
        subtotal: Decimal,
        deadline_hours: int,
        lines: list[PriceBreakdownItem],
    ) -> Decimal:
        """
        Apply deadline multiplier if a matching band exists.
        """
        deadline_rate = DeadlineRate.objects.filter(
            website=website,
            is_active=True,
            max_hours__gte=deadline_hours,
        ).order_by("max_hours").first()

        if deadline_rate is None:
            return subtotal

        return self._apply_multiplier(
            subtotal=subtotal,
            multiplier=deadline_rate.multiplier,
            lines=lines,
            code="deadline",
            label=f"Deadline ({deadline_rate.label})",
        )

    def _apply_multiplier(
        self,
        *,
        subtotal: Decimal,
        multiplier: Decimal,
        lines: list[PriceBreakdownItem],
        code: str,
        label: str,
    ) -> Decimal:
        """
        Apply a multiplier and add its delta to the breakdown.
        """
        new_total = self._money(subtotal * multiplier)
        delta = self._money(new_total - subtotal)

        if delta != Decimal("0.00"):
            lines.append(
                PriceBreakdownItem(
                    line_type=BreakdownLineType.MULTIPLIER,
                    code=code,
                    label=label,
                    amount=delta,
                    metadata={"multiplier": str(multiplier)},
                )
            )

        return new_total

    def _apply_addons(
        self,
        *,
        website,
        subtotal: Decimal,
        addon_codes: list[Any],
        lines: list[PriceBreakdownItem],
    ) -> Decimal:
        """
        Apply selected addon fees.
        """
        if not addon_codes:
            return subtotal

        codes = [
            code for code in addon_codes
            if isinstance(code, str) and code.strip()
        ]
        if not codes:
            return subtotal

        addons = ServiceAddon.objects.filter(
            website=website,
            addon_code__in=codes,
            is_active=True,
        ).order_by("sort_order", "id")

        running_total = subtotal
        for addon in addons:
            fee = self._money(addon.flat_amount)
            lines.append(
                PriceBreakdownItem(
                    line_type=BreakdownLineType.ADDON,
                    code=addon.addon_code,
                    label=addon.name,
                    amount=fee,
                )
            )
            running_total = self._money(running_total + fee)

        return running_total

    def _money(self, amount: Decimal) -> Decimal:
        """
        Normalize money values to two decimal places.
        """
        return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)