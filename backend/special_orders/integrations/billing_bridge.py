from __future__ import annotations

from typing import Any

from special_orders.models import (
    SpecialOrder,
    SpecialOrderFundingMilestone,
)
from special_orders.constants import FundingMilestoneStatus
from special_orders.models.funding import SpecialOrderFundingMilestone


class SpecialOrderBillingBridge:
    """
    Bridge special order funding milestones into billing.

    Billing owns invoices, payment requests, receipts, and statements.
    Special orders only define what is due and when.
    """

    @classmethod
    def create_invoice_for_milestone(
        cls,
        *,
        special_order: SpecialOrder,
        milestone: SpecialOrderFundingMilestone,
        created_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Create a billing invoice for a single funding milestone.

        The invoice is created in DRAFT status. Call
        InvoiceOrchestrationService.issue() to send it to the client.

        Args:
            special_order: Parent special order.
            milestone: Funding milestone to invoice.
            created_by: Staff member creating the invoice.
            metadata: Optional additional metadata stored on the invoice.

        Returns:
            Invoice: Newly created draft invoice.
        """
        from billing.services.invoice_service import InvoiceService
        from billing.constants import InvoicePurpose

        cls._validate_milestone(
            special_order=special_order,
            milestone=milestone,
        )

        sequence = getattr(milestone, "sequence", "")
        label = getattr(milestone, "label", "")
        title = f"Milestone {sequence}: {label}" if sequence else label or "Milestone payment"

        # Resolve currency — try funding plan, fall back to special order.
        currency = ""
        funding_plan = getattr(milestone, "funding_plan", None)
        if funding_plan is not None:
            currency = str(getattr(funding_plan, "currency", "") or "")
        if not currency:
            currency = str(getattr(special_order, "currency", "") or "")

        return InvoiceService.create_invoice(
            website=special_order.website,
            title=title,
            amount=milestone.amount_due,
            due_at=milestone.due_at,
            issued_by=created_by,
            purpose=InvoicePurpose.SPECIAL_ORDER,
            description=(
                f"Special order milestone payment — "
                f"{special_order.title or str(special_order.pk)}"
            ),
            client=special_order.client,
            special_order=special_order,
            currency=currency,
        )

    @classmethod
    def create_invoices_for_unpaid_milestones(
        cls,
        *,
        special_order: SpecialOrder,
        created_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> list:
        """
        Create billing records for unpaid milestones.
        """
        invoices = []

        milestones = SpecialOrderFundingMilestone.objects.filter(
            website=special_order.website,
            special_order=special_order,
            status__in=[
                FundingMilestoneStatus.PENDING,
                FundingMilestoneStatus.PARTIALLY_PAID,
            ],
        ).order_by("sequence")

        for milestone in milestones:
            invoice = cls.create_invoice_for_milestone(
                special_order=special_order,
                milestone=milestone,
                created_by=created_by,
                metadata=metadata,
            )
            invoices.append(invoice)

        return invoices

    @staticmethod
    def _validate_milestone(
        *,
        special_order: SpecialOrder,
        milestone: SpecialOrderFundingMilestone,
    ) -> None:
        """
        Ensure milestone belongs to this special order and tenant.
        """
        if milestone.website_id != special_order.website_id:
            raise ValueError("Milestone belongs to another tenant.")

        if milestone.special_order_id != special_order.id:
            raise ValueError("Milestone belongs to another special order.")