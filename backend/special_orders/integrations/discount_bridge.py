from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpecialOrderDiscountResult:
    discount_amount: Decimal
    final_amount: Decimal
    discount_reference: str
    metadata: dict[str, Any]


class SpecialOrderDiscountBridge:
    """
    Bridge special order pricing to the central discount system.

    Uses DiscountApplicationService.preview() — not apply() — because
    special orders have their own billing flow (invoice/milestone) and
    the discount usage is recorded at invoice creation time, not here.
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
        Resolve the best discount for a special order gross amount.

        Returns a zero-discount result when no code is provided or when
        the discount system is unavailable (fail-open so pricing is never
        blocked by a discount system error).
        """
        if not coupon_code:
            return SpecialOrderDiscountResult(
                discount_amount=Decimal("0.00"),
                final_amount=gross_amount,
                discount_reference="",
                metadata={},
            )

        try:
            from discounts.services.discount_application_service import (
                DiscountApplicationService,
            )

            resolved = DiscountApplicationService.preview(
                website=website,
                client=client,
                subtotal=gross_amount,
                payable_type="special_order",
                has_prior_paid_purchase=True,
                entered_code=coupon_code,
            )

            if resolved is None:
                return SpecialOrderDiscountResult(
                    discount_amount=Decimal("0.00"),
                    final_amount=gross_amount,
                    discount_reference=coupon_code,
                    metadata={"coupon_code": coupon_code, "resolved": False},
                )

            discount_amount = getattr(resolved, "discount_amount", Decimal("0.00"))
            final_amount = gross_amount - discount_amount

            return SpecialOrderDiscountResult(
                discount_amount=discount_amount,
                final_amount=max(Decimal("0.00"), final_amount),
                discount_reference=getattr(resolved, "discount_code", coupon_code) or coupon_code,
                metadata={
                    "coupon_code": coupon_code,
                    "discount_id": getattr(resolved, "discount_id", None),
                    **(metadata or {}),
                },
            )

        except Exception as exc:
            log.warning(
                "SpecialOrderDiscountBridge.apply_discount failed "
                "coupon=%s: %s — proceeding without discount.",
                coupon_code,
                exc,
            )
            return SpecialOrderDiscountResult(
                discount_amount=Decimal("0.00"),
                final_amount=gross_amount,
                discount_reference="",
                metadata={"coupon_code": coupon_code, "error": str(exc)},
            )
