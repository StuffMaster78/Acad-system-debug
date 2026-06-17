from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.utils import timezone


class OrderForfeitureCalculatorService:
    """
    Calculate the forfeiture percentage (0–80 %) for a cancellation request
    based on how close the order deadline is.

    Tiers (deadline from now):
        > 7 days        →  0 %
        3–7 days        → 20 %
        1–3 days        → 40 %
        < 24 hours      → 80 %

    Orders that have not been started (ready_for_staffing) always forfeit 0 %.
    """

    TIERS = [
        (7 * 24 * 60 * 60, Decimal("0.00")),
        (3 * 24 * 60 * 60, Decimal("20.00")),
        (1 * 24 * 60 * 60, Decimal("40.00")),
        (0, Decimal("80.00")),
    ]

    @classmethod
    def calculate(cls, *, order) -> tuple[Decimal, Decimal, Decimal]:
        """
        Return (forfeiture_pct, forfeiture_amount, refund_amount).

        If the order has no deadline or no paid amount, returns zeros.
        """
        from orders.models.orders.enums import OrderStatus

        if order.status == OrderStatus.READY_FOR_STAFFING:
            return Decimal("0.00"), Decimal("0.00"), cls._paid(order)

        deadline = getattr(order, "deadline", None)
        if deadline is None:
            return Decimal("0.00"), Decimal("0.00"), cls._paid(order)

        seconds_until_deadline = (deadline - timezone.now()).total_seconds()
        pct = cls._tier_pct(seconds_until_deadline)

        paid = cls._paid(order)
        forfeiture = (pct / Decimal("100")) * paid
        refund = paid - forfeiture

        return pct, forfeiture.quantize(Decimal("0.01")), refund.quantize(Decimal("0.01"))

    @classmethod
    def _tier_pct(cls, seconds: float) -> Decimal:
        for threshold_secs, pct in cls.TIERS:
            if seconds > threshold_secs:
                return pct
        return Decimal("80.00")

    @staticmethod
    def _paid(order) -> Decimal:
        val = getattr(order, "amount_paid", None)
        if val is None:
            return Decimal("0.00")
        return Decimal(str(val))
