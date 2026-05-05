from __future__ import annotations

from decimal import Decimal

from discounts.constants import PayableType
from discounts.integrations import DiscountDomainAdapter
from discounts.integrations import DiscountPayableContext


class SpecialOrderDiscountIntegrationService:
    """
    Bridge special orders to the discounts app.
    """

    @staticmethod
    def apply_special_order_discount(
        *,
        special_order,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool,
    ):
        """
        Apply discount to a special order quote.
        """
        context = DiscountPayableContext(
            website=special_order.website,
            client=special_order.client,
            subtotal=special_order.quote_amount,
            payable_type=PayableType.SPECIAL_ORDER,
            payable_id=str(special_order.pk),
            has_prior_paid_purchase=has_prior_paid_purchase,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            metadata={
                "source": "special_orders",
                "special_order_id": special_order.pk,
            },
        )

        result = DiscountDomainAdapter.apply_discount(
            context=context,
        )

        special_order.discount_code = result.discount_code or ""
        special_order.discount_amount = result.discount_amount
        special_order.final_amount = result.final_amount
        special_order.save(
            update_fields=[
                "discount_code",
                "discount_amount",
                "final_amount",
                "updated_at",
            ]
        )

        return result