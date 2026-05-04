from __future__ import annotations

from typing import Any

from class_management.models.class_order import ClassOrder
from class_management.services.class_payment_service import (
    ClassPaymentService,
)


class ClassBillingIntegrationService:
    """
    Bridge class orders to the billing app.

    Billing owns invoices. Class management only links the created invoice
    back to the class order through ClassInvoiceLink.
    """

    @staticmethod
    def create_invoice_for_class_order(
        *,
        class_order: ClassOrder,
        issued_by,
        due_at,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Create a billing invoice for an accepted class order.
        """
        from billing.constants import InvoicePurpose
        from billing.services.invoice_service import InvoiceService

        invoice = InvoiceService.create_invoice(
            website=class_order.website,
            title=f"Class Order #{class_order.pk}: {class_order.title}",
            amount=class_order.balance_amount,
            due_at=due_at,
            issued_by=issued_by,
            purpose=InvoicePurpose.OTHER,
            description=(
                "Invoice for class order "
                f"#{class_order.pk}: {class_order.title}"
            ),
            client=class_order.client,
            currency=class_order.currency,
            order_number=f"class-{class_order.pk}",
        )

        ClassPaymentService.create_invoice_link(
            class_order=class_order,
            invoice_id=str(invoice.pk),
            invoice_number=getattr(invoice, "invoice_number", ""),
            status=getattr(invoice, "status", ""),
            metadata={
                **(metadata or {}),
                "source": "billing",
                "class_order_id": str(class_order.pk),
            },
        )

        return invoice