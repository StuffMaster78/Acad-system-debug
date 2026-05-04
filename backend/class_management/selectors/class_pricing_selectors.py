from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import ClassPriceProposal


class ClassPricingSelector:
    """
    Read/query helpers for class price proposals.
    """

    @staticmethod
    def proposals_for_order(*, class_order) -> QuerySet[ClassPriceProposal]:
        return (
            ClassPriceProposal.objects.filter(class_order=class_order)
            .select_related("proposed_by", "accepted_by")
            .prefetch_related("counter_offers")
            .order_by("-created_at")
        )

    @staticmethod
    def latest_active_proposal(*, class_order) -> ClassPriceProposal | None:
        return (
            ClassPriceProposal.objects.filter(
                class_order=class_order,
                status__in=["sent", "countered"],
            )
            .order_by("-created_at")
            .first()
        )