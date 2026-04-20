"""
Base calculator contracts for the order_pricing_core app.

These classes define the shared calculator result shapes used by the
paper order, design order, and diagram order calculators.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class PriceBreakdownItem:
    """
    Represents one internal pricing breakdown line.
    """

    line_type: str
    code: str
    label: str
    amount: Decimal
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PriceCalculationResult:
    """
    Represents the result of a pricing calculation.
    """

    subtotal: Decimal
    discount_amount: Decimal
    total: Decimal
    lines: list[PriceBreakdownItem]
    metadata: dict[str, Any] = field(default_factory=dict)
    suggestions: list[dict[str, Any]] = field(default_factory=list)


class BasePricingCalculator:
    """
    Base class for all pricing calculators.

    Concrete calculators must implement the calculate method.
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
        Calculate a price result for the supplied payload.
        """
        raise NotImplementedError(
            "Subclasses must implement calculate()."
        )