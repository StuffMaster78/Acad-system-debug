from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from special_orders.constants import (
    ChangeRequestPricingImpact,
    ChangeRequestStatus,
    FundingMilestoneType,
)
from special_orders.models import (
    SpecialOrder,
    SpecialOrderChangeRequest,
    SpecialOrderChangeRequestQuote,
    SpecialOrderFundingMilestone,
)
from special_orders.selectors import SpecialOrderFundingSelector


class SpecialOrderChangeRequestService:
    """
    Handle special order scope change requests.

    If accepted and billable, the service creates a new funding milestone.
    It does not mutate the original quote or pricing snapshot.
    """

    @classmethod
    @transaction.atomic
    def create_request(
        cls,
        *,
        special_order: SpecialOrder,
        requested_by,
        title: str,
        description: str,
        pricing_impact: str = ChangeRequestPricingImpact.ADDITIONAL_CHARGE,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderChangeRequest:
        """
        Create a client or staff scope change request.
        """
        if not title.strip():
            raise ValueError("Change request title is required.")

        if not description.strip():
            raise ValueError("Change request description is required.")

        return SpecialOrderChangeRequest.objects.create(
            website=special_order.website,
            special_order=special_order,
            status=ChangeRequestStatus.PENDING,
            pricing_impact=pricing_impact,
            title=title.strip(),
            description=description.strip(),
            requested_by=requested_by,
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def review_request(
        cls,
        *,
        change_request: SpecialOrderChangeRequest,
        reviewed_by,
        approve: bool,
        decision_reason: str = "",
        estimated_amount: Decimal | None = None,
    ) -> SpecialOrderChangeRequest:
        """
        Approve or reject a change request.
        """
        change_request = cls._lock_request(change_request=change_request)

        if change_request.status != ChangeRequestStatus.PENDING:
            raise ValueError("Only pending change requests can be reviewed.")

        change_request.reviewed_by = reviewed_by
        change_request.reviewed_at = timezone.now()
        change_request.decision_reason = decision_reason
        change_request.estimated_amount = estimated_amount
        change_request.status = (
            ChangeRequestStatus.APPROVED
            if approve
            else ChangeRequestStatus.REJECTED
        )
        change_request.save(
            update_fields=[
                "reviewed_by",
                "reviewed_at",
                "decision_reason",
                "estimated_amount",
                "status",
                "updated_at",
            ]
        )

        return change_request

    @classmethod
    @transaction.atomic
    def create_change_quote(
        cls,
        *,
        change_request: SpecialOrderChangeRequest,
        amount: Decimal,
        created_by,
        expires_at=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderChangeRequestQuote:
        """
        Create quote for an approved billable change request.
        """
        change_request = cls._lock_request(change_request=change_request)

        if change_request.status != ChangeRequestStatus.APPROVED:
            raise ValueError("Only approved change requests can be quoted.")

        if (
            change_request.pricing_impact
            != ChangeRequestPricingImpact.ADDITIONAL_CHARGE
        ):
            raise ValueError(
                "Only additional-charge change requests require quotes."
            )

        if amount <= Decimal("0.00"):
            raise ValueError("Change quote amount must be greater than zero.")

        existing_quote = SpecialOrderChangeRequestQuote.objects.filter(
            website=change_request.website,
            change_request=change_request,
        ).first()

        if existing_quote is not None:
            raise ValueError("Change request already has a quote.")

        quote = SpecialOrderChangeRequestQuote.objects.create(
            website=change_request.website,
            change_request=change_request,
            amount=amount,
            currency=change_request.special_order.currency,
            expires_at=expires_at,
            created_by=created_by,
            metadata=metadata or {},
        )

        change_request.status = ChangeRequestStatus.QUOTED
        change_request.approved_amount = amount
        change_request.save(
            update_fields=[
                "status",
                "approved_amount",
                "updated_at",
            ]
        )

        return quote

    @classmethod
    @transaction.atomic
    def accept_change_quote(
        cls,
        *,
        quote: SpecialOrderChangeRequestQuote,
        accepted_by,
    ) -> SpecialOrderFundingMilestone:
        """
        Accept a change request quote and create a funding milestone.
        """
        quote = SpecialOrderChangeRequestQuote.objects.select_for_update().get(
            id=quote.id,
            website=quote.website,
        )
        change_request = cls._lock_request(
            change_request=quote.change_request,
        )

        if change_request.status != ChangeRequestStatus.QUOTED:
            raise ValueError("Only quoted change requests can be accepted.")

        if quote.expires_at and quote.expires_at <= timezone.now():
            raise ValueError("Change request quote has expired.")

        funding_plan = SpecialOrderFundingSelector.get_plan(
            website=change_request.website,
            special_order=change_request.special_order,
        )
        funding_plan.total_amount += quote.amount
        funding_plan.save(
            update_fields=[
                "total_amount",
                "updated_at",
            ]
        )

        last_sequence = (
            SpecialOrderFundingMilestone.objects.filter(
                website=change_request.website,
                funding_plan=funding_plan,
            )
            .order_by("-sequence")
            .values_list("sequence", flat=True)
            .first()
            or 0
        )

        milestone = SpecialOrderFundingMilestone.objects.create(
            website=change_request.website,
            funding_plan=funding_plan,
            special_order=change_request.special_order,
            milestone_type=FundingMilestoneType.CHANGE_REQUEST,
            sequence=last_sequence + 1,
            label=f"Change request: {change_request.title}",
            amount_due=quote.amount,
            required_before_delivery=True,
            metadata={
                "change_request_id": change_request.id,
                "change_quote_id": quote.id,
            },
        )

        quote.accepted_at = timezone.now()
        quote.save(
            update_fields=[
                "accepted_at",
                "updated_at",
            ]
        )

        change_request.status = ChangeRequestStatus.ACCEPTED
        change_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return milestone

    @staticmethod
    def _lock_request(
        *,
        change_request: SpecialOrderChangeRequest,
    ) -> SpecialOrderChangeRequest:
        """
        Lock change request row.
        """
        return SpecialOrderChangeRequest.objects.select_for_update().get(
            id=change_request.id,
            website=change_request.website,
        )