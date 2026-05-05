from __future__ import annotations

from django.db.models import QuerySet

from special_orders.models import (
    SpecialOrderFundingMilestone,
    SpecialOrderFundingPlan,
    SpecialOrderPaymentApplication,
    SpecialOrderRefundApplication,
)


class SpecialOrderFundingSelector:
    """
    Tenant-safe read layer for funding, payments, and refunds.
    """

    @staticmethod
    def get_plan(*, website, special_order) -> SpecialOrderFundingPlan:
        return (
            SpecialOrderFundingPlan.objects.select_related(
                "special_order",
                "locked_by",
            )
            .get(
                website=website,
                special_order=special_order,
            )
        )

    @staticmethod
    def get_plan_with_milestones(
        *,
        website,
        special_order,
    ) -> SpecialOrderFundingPlan:
        return (
            SpecialOrderFundingPlan.objects.select_related(
                "special_order",
                "locked_by",
            )
            .prefetch_related("milestones")
            .get(
                website=website,
                special_order=special_order,
            )
        )

    @staticmethod
    def list_milestones(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderFundingMilestone]:
        return (
            SpecialOrderFundingMilestone.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related("funding_plan")
            .order_by("sequence")
        )

    @staticmethod
    def get_milestone(
        *,
        website,
        milestone_id: int,
    ) -> SpecialOrderFundingMilestone:
        return (
            SpecialOrderFundingMilestone.objects.select_related(
                "funding_plan",
                "special_order",
            )
            .get(
                id=milestone_id,
                website=website,
            )
        )

    @staticmethod
    def list_payment_applications(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderPaymentApplication]:
        return (
            SpecialOrderPaymentApplication.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related(
                "funding_plan",
                "milestone",
                "applied_by",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_payment_application(
        *,
        website,
        payment_application_id: int,
    ) -> SpecialOrderPaymentApplication:
        return (
            SpecialOrderPaymentApplication.objects.select_related(
                "special_order",
                "funding_plan",
                "milestone",
                "applied_by",
            )
            .get(
                id=payment_application_id,
                website=website,
            )
        )

    @staticmethod
    def list_refund_applications(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderRefundApplication]:
        return (
            SpecialOrderRefundApplication.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related(
                "funding_plan",
                "milestone",
                "original_payment_application",
                "requested_by",
                "approved_by",
            )
            .order_by("-created_at")
        )