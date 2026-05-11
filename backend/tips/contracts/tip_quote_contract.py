from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TipQuoteContract:
    """
    Immutable UX-facing tip preview response.
    """

    gross_amount: Decimal
    writer_amount: Decimal
    platform_amount: Decimal
    currency: str