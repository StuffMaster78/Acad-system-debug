from __future__ import annotations

from decimal import Decimal

from discounts.integrations.discount_payable_context import (
    DiscountPayableContext,
)
from discounts.integrations.discount_receipt_dto import DiscountReceiptDTO
from discounts.services.discount_application_service import (
    DiscountApplicationService,
)


class DiscountDomainAdapter:
    """
    Stable integration adapter for domain apps.

    Orders, classes, special orders, invoices, and payment apps should call
    this adapter instead of calling discount internals directly.
    """

    @staticmethod
    def preview_discount(
        *,
        context: DiscountPayableContext,
    ) -> DiscountReceiptDTO:
        """
        Preview discount impact without persisting usage.
        """
        resolved = DiscountApplicationService.preview(
            website=context.website,
            client=context.client,
            subtotal=context.subtotal,
            payable_type=context.payable_type,
            has_prior_paid_purchase=context.has_prior_paid_purchase,
            entered_code=context.entered_code,
            lifetime_spend=context.lifetime_spend,
        )

        if resolved is None:
            return DiscountReceiptDTO(
                discount_code=None,
                discount_amount=Decimal("0.00"),
                final_amount=context.subtotal,
                origin=None,
                usage_id=None,
                applied=False,
            )

        return DiscountReceiptDTO(
            discount_code=resolved.discount_code,
            discount_amount=resolved.discount_amount,
            final_amount=resolved.final_amount,
            origin=resolved.origin,
            usage_id=None,
            applied=False,
        )

    @staticmethod
    def apply_discount(
        *,
        context: DiscountPayableContext,
    ) -> DiscountReceiptDTO:
        """
        Apply discount and persist immutable usage.
        """
        usage = DiscountApplicationService.apply(
            website=context.website,
            client=context.client,
            subtotal=context.subtotal,
            payable_type=context.payable_type,
            payable_id=context.payable_id,
            has_prior_paid_purchase=context.has_prior_paid_purchase,
            entered_code=context.entered_code,
            lifetime_spend=context.lifetime_spend,
            metadata=context.metadata,
        )

        if usage is None:
            return DiscountReceiptDTO(
                discount_code=None,
                discount_amount=Decimal("0.00"),
                final_amount=context.subtotal,
                origin=None,
                usage_id=None,
                applied=False,
            )

        return DiscountReceiptDTO(
            discount_code=usage.discount_code,
            discount_amount=usage.discount_amount,
            final_amount=usage.final_amount,
            origin=usage.origin,
            usage_id=usage.pk,
            applied=True,
        )