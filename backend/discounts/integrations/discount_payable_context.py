from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DiscountPayableContext:
    """
    Normalized payable data passed from domain apps into discounts.
    """

    website: object
    client: object
    subtotal: Decimal
    payable_type: str
    payable_id: str
    has_prior_paid_purchase: bool
    entered_code: str | None = None
    lifetime_spend: Decimal | None = None
    metadata: dict | None = None