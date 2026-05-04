from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from class_management.constants import ClassProposalStatus
from class_management.exceptions import ClassPricingError


class ClassPricingValidator:
    @staticmethod
    def validate_amounts(
        *,
        amount: Decimal,
        discount_amount: Decimal,
    ) -> None:
        if amount <= Decimal("0.00"):
            raise ClassPricingError(
                "Proposal amount must be greater than zero."
            )

        if discount_amount < Decimal("0.00"):
            raise ClassPricingError(
                "Discount amount cannot be negative."
            )

        if discount_amount >= amount:
            raise ClassPricingError(
                "Discount amount must be less than proposal amount."
            )

    @staticmethod
    def require_active_proposal(*, proposal) -> None:
        if proposal.status not in {
            ClassProposalStatus.SENT,
            ClassProposalStatus.COUNTERED,
        }:
            raise ClassPricingError(
                "Only sent or countered proposals can be used."
            )

    @staticmethod
    def require_not_expired(*, proposal) -> None:
        if proposal.expires_at and proposal.expires_at <= timezone.now():
            raise ClassPricingError(
                "This price proposal has expired."
            )