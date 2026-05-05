from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DiscountReceiptDTO:
    """
    Domain-safe discount result returned to orders/classes/special orders.
    """

    discount_code: str | None
    discount_amount: Decimal
    final_amount: Decimal
    origin: str | None
    usage_id: int | None
    applied: bool