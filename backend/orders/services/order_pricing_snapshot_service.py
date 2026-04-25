from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.db import transaction

from orders.models import Order
from orders.models.orders.order_pricing_snapshot import (
    OrderPricingSnapshot,
)


class OrderPricingSnapshotService:
    """
    Own order-side frozen pricing history.

    Responsibilities:
        1. Persist an order-owned pricing snapshot record.
        2. Mark older snapshots as non-current.
        3. Mirror commercial values from pricing core into order history.

    Notes:
        1. Order.pricing_snapshot points to the upstream pricing-core
           snapshot used for the current commercial state.
        2. OrderPricingSnapshot is the order-owned historical ledger of
           pricing state over time.
    """

    @classmethod
    @transaction.atomic
    def record_current_snapshot(
        cls,
        *,
        order: Order,
        source_pricing_snapshot: Optional[Any],
        subtotal_amount: Decimal,
        discount_amount: Decimal,
        total_amount: Decimal,
        writer_compensation_amount: Decimal,
        pricing_payload: dict[str, Any],
        created_by: Optional[Any] = None,
        currency: str = "",
        pricing_policy_version: str = "",
    ) -> OrderPricingSnapshot:
        """
        Persist a new current order pricing snapshot and retire older ones.
        """
        OrderPricingSnapshot.objects.filter(
            order=order,
            is_current=True,
        ).update(is_current=False)

        snapshot = OrderPricingSnapshot.objects.create(
            website=order.website,
            order=order,
            source_pricing_snapshot=source_pricing_snapshot,
            is_current=True,
            currency=currency or getattr(order, "currency", ""),
            pricing_policy_version=pricing_policy_version,
            subtotal_amount=subtotal_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            writer_compensation_amount=writer_compensation_amount,
            pricing_payload=pricing_payload,
            created_by=created_by,
        )
        return snapshot