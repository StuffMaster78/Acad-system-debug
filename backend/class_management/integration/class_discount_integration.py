from __future__ import annotations

from decimal import Decimal
from typing import Any

from discounts.constants import PayableType
from discounts.integrations import DiscountDomainAdapter
from discounts.integrations import DiscountPayableContext


class ClassDiscountIntegrationService:
    """
    Bridge class orders to the discounts app.
    """

    @staticmethod
    def preview_class_discount(
        *,
        class_order,
        subtotal: Decimal,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool,
    ):
        """
        Preview discount impact without recording usage.
        """
        context = ClassDiscountIntegrationService._build_context(
            class_order=class_order,
            subtotal=subtotal,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            has_prior_paid_purchase=has_prior_paid_purchase,
        )

        return DiscountDomainAdapter.preview_discount(context=context)

    @staticmethod
    def apply_class_discount(
        *,
        class_order,
        subtotal: Decimal | None = None,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool,
    ):
        """
        Apply discount and persist class order discount fields.
        """
        effective_subtotal = subtotal or class_order.quoted_amount

        context = ClassDiscountIntegrationService._build_context(
            class_order=class_order,
            subtotal=effective_subtotal,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            has_prior_paid_purchase=has_prior_paid_purchase,
        )

        result = DiscountDomainAdapter.apply_discount(context=context)

        class_order.discount_code = result.discount_code or ""
        class_order.discount_amount = result.discount_amount
        class_order.final_amount = result.final_amount
        class_order.balance_amount = result.final_amount
        class_order.discount_snapshot = {
            "discount_code": result.discount_code,
            "discount_amount": str(result.discount_amount),
            "final_amount": str(result.final_amount),
        }
        class_order.save(
            update_fields=[
                "discount_code",
                "discount_amount",
                "final_amount",
                "balance_amount",
                "discount_snapshot",
                "updated_at",
            ],
        )

        return result

    @staticmethod
    def _build_context(
        *,
        class_order,
        subtotal: Decimal,
        entered_code: str | None,
        lifetime_spend: Decimal | None,
        has_prior_paid_purchase: bool,
    ) -> DiscountPayableContext:
        """
        Build the discounts app payable context for a class order.
        """
        class_order_pk = ClassDiscountIntegrationService._get_pk(class_order)

        return DiscountPayableContext(
            website=class_order.website,
            client=class_order.client,
            subtotal=subtotal,
            payable_type=PayableType.CLASS_ORDER,
            payable_id=str(class_order_pk),
            has_prior_paid_purchase=has_prior_paid_purchase,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            metadata={
                "source": "classes",
                "class_order_id": str(class_order_pk),
            },
        )

    @staticmethod
    def _get_pk(obj: Any) -> Any:
        """
        Return an object's primary key safely.
        """
        return getattr(obj, "pk", None)