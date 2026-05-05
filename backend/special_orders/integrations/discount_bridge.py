# special_orders/integrations/discount_bridge.py

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class SpecialOrderDiscountResult:
    discount_amount: Decimal
    final_amount: Decimal
    discount_reference: str
    metadata: dict[str, Any]


class SpecialOrderDiscountBridge:
    """
    Bridge special order pricing to the central discount system.

    Replace the placeholder logic with your real central DiscountService.
    """

    @classmethod
    def apply_discount(
        cls,
        *,
        website,
        client,
        gross_amount: Decimal,
        currency: str,
        coupon_code: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderDiscountResult:
        """
        Apply central discounts to a gross special order amount.
        """
        if not coupon_code:
            return SpecialOrderDiscountResult(
                discount_amount=Decimal("0.00"),
                final_amount=gross_amount,
                discount_reference="",
                metadata={},
            )

        # Future shape:
        #
        # result = DiscountService.apply(
        #     website=website,
        #     client=client,
        #     amount=gross_amount,
        #     currency=currency,
        #     code=coupon_code,
        #     context={
        #         "source_app": "special_orders",
        #         **(metadata or {}),
        #     },
        # )
        #
        # return SpecialOrderDiscountResult(
        #     discount_amount=result.discount_amount,
        #     final_amount=result.final_amount,
        #     discount_reference=result.reference,
        #     metadata=result.metadata,
        # )

        return SpecialOrderDiscountResult(
            discount_amount=Decimal("0.00"),
            final_amount=gross_amount,
            discount_reference="",
            metadata={
                "coupon_code": coupon_code,
                "discount_not_yet_wired": True,
                **(metadata or {}),
            },
        )