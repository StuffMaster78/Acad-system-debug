"""
Diagram order calculator for the order_pricing_core app.
"""

from __future__ import annotations

from decimal import Decimal
from decimal import ROUND_HALF_UP
from typing import Any

from django.core.exceptions import ValidationError

from order_pricing_core.calculators.base import BasePricingCalculator
from order_pricing_core.calculators.base import PriceBreakdownItem
from order_pricing_core.calculators.base import PriceCalculationResult
from order_pricing_core.constants import BreakdownLineType
from order_pricing_core.constants import QuoteMode
from order_pricing_core.models import DeadlineRate
from order_pricing_core.models import DiagramComplexityRate
from order_pricing_core.models import ServiceAddon
from order_pricing_core.models import WebsitePricingProfile
from order_pricing_core.validators.quote_input_validators import (
    optional_positive_int,
)
from order_pricing_core.validators.quote_input_validators import (
    require_positive_int,
)
from order_pricing_core.validators.quote_input_validators import (
    require_string,
)

TWOPLACES = Decimal("0.01")


class DiagramOrderPricingCalculator(BasePricingCalculator):
    """
    Calculator for standardized diagram-order services.
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
        Calculate a price result for a diagram-order service.
        """
        if mode not in {QuoteMode.ESTIMATE, QuoteMode.FINAL}:
            raise ValidationError({"mode": "Unsupported quote mode."})

        profile = WebsitePricingProfile.objects.get(
            website=website,
            is_active=True,
        )

        quantity = require_positive_int(payload, "quantity", "Quantity")
        deadline_hours = optional_positive_int(payload, "deadline_hours")

        if mode == QuoteMode.ESTIMATE:
            return self._estimate_result(
                profile=profile,
                quantity=quantity,
                deadline_hours=deadline_hours,
            )

        addon_codes = payload.get("selected_addon_codes", [])

        return self._final_result(
            website=website,
            service=service,
            profile=profile,
            quantity=quantity,
            deadline_hours=deadline_hours,
            complexity=require_string(
                payload,
                "diagram_complexity",
                "Diagram complexity",
            ),
            diagram_type=require_string(
                payload,
                "diagram_type",
                "Diagram type",
            ),
            addon_codes=addon_codes,
        )

    def _estimate_result(
        self,
        *,
        profile: WebsitePricingProfile,
        quantity: int,
        deadline_hours: int | None,
    ) -> PriceCalculationResult:
        """
        Build an estimate-mode result for diagram work.
        """
        base_amount = self._money(
            Decimal(quantity) * profile.base_price_per_diagram
        )

        min_total = self._money(
            max(base_amount, profile.minimum_diagram_order_charge)
        )

        max_multiplier = Decimal("1.5000")
        if deadline_hours is not None and deadline_hours <= 24:
            max_multiplier = Decimal("1.8000")

        max_total = self._money(
            max(
                self._money(base_amount * max_multiplier),
                profile.minimum_diagram_order_charge,
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
            },
            suggestions=[],
        )

    def _final_result(
        self,
        *,
        website,
        service,
        profile: WebsitePricingProfile,
        quantity: int,
        deadline_hours: int | None,
        complexity: str,
        diagram_type: str,
        addon_codes: list[Any],
    ) -> PriceCalculationResult:
        """
        Build the final calculated diagram-order result.
        """
        complexity_rate = DiagramComplexityRate.objects.get(
            website=website,
            complexity=complexity,
            is_active=True,
        )

        lines: list[PriceBreakdownItem] = []

        base_amount = self._money(
            Decimal(quantity) * profile.base_price_per_diagram
        )
        lines.append(
            PriceBreakdownItem(
                line_type=BreakdownLineType.BASE,
                code="diagram_base",
                label=f"Base price for {quantity} diagrams",
                amount=base_amount,
                metadata={"diagram_type": diagram_type},
            )
        )

        subtotal = base_amount

        subtotal = self._apply_multiplier(
            subtotal=subtotal,
            multiplier=complexity_rate.multiplier,
            lines=lines,
            code="diagram_complexity",
            label=f"Diagram complexity ({complexity})",
        )

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
            max(subtotal, profile.minimum_diagram_order_charge)
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
                "diagram_complexity": complexity,
                "diagram_type": diagram_type,
                "addon_codes": addon_codes,
            },
            suggestions=[],
        )

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