from __future__ import annotations

from decimal import Decimal

from discounts.integrations import DiscountDomainAdapter
from discounts.integrations import DiscountPayableContext


class InvoiceDiscountIntegrationService:
    """
    Bridge invoices to the discounts app.

    Billing owns invoices. Discounts only compute and persist discount usage.
    """

    @staticmethod
    def preview_invoice_discount(
        *,
        invoice,
        payable_type: str,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool,
    ):
        """
        Preview discount impact for an invoice.
        """
        context = InvoiceDiscountIntegrationService._build_context(
            invoice=invoice,
            payable_type=payable_type,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            has_prior_paid_purchase=has_prior_paid_purchase,
        )

        return DiscountDomainAdapter.preview_discount(context=context)

    @staticmethod
    def apply_invoice_discount(
        *,
        invoice,
        payable_type: str,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool,
    ):
        """
        Apply discount and persist invoice final payable amount.
        """
        if invoice.original_amount is None:
            invoice.original_amount = invoice.amount
            invoice.save(
                update_fields=[
                    "original_amount",
                    "updated_at",
                ]
            )

        context = InvoiceDiscountIntegrationService._build_context(
            invoice=invoice,
            payable_type=payable_type,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            has_prior_paid_purchase=has_prior_paid_purchase,
        )

        result = DiscountDomainAdapter.apply_discount(context=context)

        invoice.discount_code = result.discount_code or ""
        invoice.discount_amount = result.discount_amount
        invoice.total_amount = result.final_amount
        invoice.save(
            update_fields=[
                "discount_code",
                "discount_amount",
                "discount_usage_id",
                "amount",
                "updated_at",
            ]
        )

        return result

    @staticmethod
    def _build_context(
        *,
        invoice,
        payable_type: str,
        entered_code: str | None,
        lifetime_spend: Decimal | None,
        has_prior_paid_purchase: bool,
    ) -> DiscountPayableContext:
        """
        Build normalized discount context from an invoice.
        """
        subtotal = invoice.original_amount or invoice.amount

        return DiscountPayableContext(
            website=invoice.website,
            client=invoice.client,
            subtotal=subtotal,
            payable_type=payable_type,
            payable_id=str(invoice.pk),
            has_prior_paid_purchase=has_prior_paid_purchase,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
            metadata={
                "source": "billing",
                "invoice_id": invoice.pk,
                "invoice_number": getattr(invoice, "invoice_number", ""),
                "invoice_reference": invoice.reference,
            },
        )