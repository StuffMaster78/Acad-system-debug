from __future__ import annotations

from decimal import Decimal

from discounts.constants import PayableType
from discounts.integrations import DiscountDomainAdapter
from discounts.integrations import DiscountPayableContext


class OrderDiscountIntegrationService:
    """
    Bridge orders to the discounts app.

    Orders should not call discount internals directly.
    """

    @staticmethod
    def preview_order_discount(
        *,
        order,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool,
    ):
        """
        Preview discount impact for an order.
        """
        context = DiscountPayableContext(
            website=order.website,
            client=order.client,
            subtotal=order.subtotal_amount,
            payable_type=PayableType.ORDER,
            payable_id=str(order.pk),
            has_prior_paid_purchase=has_prior_paid_purchase,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            metadata={
                "source": "orders",
                "order_id": order.pk,
            },
        )

        return DiscountDomainAdapter.preview_discount(
            context=context,
        )

    @staticmethod
    def apply_order_discount(
        *,
        order,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool,
    ):
        """
        Apply discount and persist order discount totals.
        """
        context = DiscountPayableContext(
            website=order.website,
            client=order.client,
            subtotal=order.subtotal_amount,
            payable_type=PayableType.ORDER,
            payable_id=str(order.pk),
            has_prior_paid_purchase=has_prior_paid_purchase,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            metadata={
                "source": "orders",
                "order_id": order.pk,
            },
        )

        result = DiscountDomainAdapter.apply_discount(
            context=context,
        )

        order.discount_code = result.discount_code or ""
        order.discount_amount = result.discount_amount
        order.total_amount = result.final_amount
        order.save(
            update_fields=[
                "discount_code",
                "discount_amount",
                "total_amount",
                "updated_at",
            ]
        )

        return result