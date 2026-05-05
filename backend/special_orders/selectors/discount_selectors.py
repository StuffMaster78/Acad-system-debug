from __future__ import annotations

from django.db.models import QuerySet

from special_orders.models import (
    SpecialOrderDiscountApplication,
    SpecialOrderDiscountRule,
)


class SpecialOrderDiscountSelector:
    """
    Tenant-safe read layer for discount rules and applications.
    """

    @staticmethod
    def list_rules(
        *,
        website,
        active_only: bool = True,
    ) -> QuerySet[SpecialOrderDiscountRule]:
        queryset = SpecialOrderDiscountRule.objects.filter(
            website=website,
        ).order_by("name")

        if active_only:
            queryset = queryset.filter(status="active")

        return queryset

    @staticmethod
    def get_rule_by_code(
        *,
        website,
        code: str,
    ) -> SpecialOrderDiscountRule:
        return SpecialOrderDiscountRule.objects.get(
            website=website,
            code=code,
        )

    @staticmethod
    def list_applications_for_order(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderDiscountApplication]:
        return (
            SpecialOrderDiscountApplication.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related(
                "quote",
                "discount_rule",
                "approved_by",
                "applied_by",
            )
            .order_by("-created_at")
        )