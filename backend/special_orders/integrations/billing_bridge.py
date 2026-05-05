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
        Create a billing invoice or payment request for one milestone.

        Replace the placeholder body with your actual billing service call.
        """
        cls._validate_milestone(
            special_order=special_order,
            milestone=milestone,
        )

        # Example shape only:
        #
        # return BillingInvoiceService.create_invoice(
        #     website=special_order.website,
        #     client=special_order.client,
        #     amount=milestone.amount_due,
        #     currency=milestone.funding_plan.currency,
        #     title=f"Special order milestone: {milestone.label}",
        #     payable=special_order,
        #     due_at=milestone.due_at,
        #     created_by=created_by,
        #     metadata={
        #         "payable_type": "special_order",
        #         "special_order_id": special_order.id,
        #         "funding_plan_id": milestone.funding_plan_id,
        #         "milestone_id": milestone.id,
        #         **(metadata or {}),
        #     },
        # )

        raise NotImplementedError(
            "Wire this to your billing invoice/payment request service."
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