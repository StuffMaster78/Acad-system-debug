from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderFundingSnapshot:
    """
    Payment status snapshot returned by the payments processor layer.
    """

    is_fully_paid: bool
    is_partially_paid: bool
    outstanding_amount: Decimal
    total_paid: Decimal
    can_activate_order: bool


class UnpaidOrderStatusService:
    """
    Adapter service for unpaid order eligibility checks.

    This service should depend on a clean read contract exposed by the
    payments processor domain. Replace the placeholder implementation
    with your actual payment snapshot integration.
    """

    @staticmethod
    def get_order_funding_snapshot(*, order) -> OrderFundingSnapshot:
        """
        Return payment funding state for an order.

        Replace this implementation with the payments processor read
        service that already knows wallet and external allocations.
        """
        total_paid = Decimal("0.00")
        total_price = getattr(order, "total_price", Decimal("0.00"))
        outstanding_amount = total_price - total_paid
        is_fully_paid = outstanding_amount <= Decimal("0.00")

        return OrderFundingSnapshot(
            is_fully_paid=is_fully_paid,
            is_partially_paid=total_paid > Decimal("0.00"),
            outstanding_amount=max(outstanding_amount, Decimal("0.00")),
            total_paid=total_paid,
            can_activate_order=is_fully_paid,
        )