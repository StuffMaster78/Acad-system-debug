from __future__ import annotations

from django.db.models import QuerySet

from special_orders.models import (
    SpecialOrderPricingSnapshot,
    SpecialOrderQuote,
)


class SpecialOrderQuoteSelector:
    """
    Tenant-safe read layer for quotes and pricing snapshots.
    """

    @staticmethod
    def get_by_id(*, website, quote_id: int) -> SpecialOrderQuote:
        return (
            SpecialOrderQuote.objects.select_related(
                "special_order",
                "created_by",
            )
            .prefetch_related("lines", "discount_applications")
            .get(
                id=quote_id,
                website=website,
            )
        )

    @staticmethod
    def get_for_order(*, website, special_order) -> SpecialOrderQuote:
        return (
            SpecialOrderQuote.objects.select_related(
                "special_order",
                "created_by",
            )
            .prefetch_related("lines")
            .get(
                website=website,
                special_order=special_order,
            )
        )

    @staticmethod
    def list_for_order(*, website, special_order) -> QuerySet[SpecialOrderQuote]:
        return (
            SpecialOrderQuote.objects.filter(
                website=website,
                special_order=special_order,
            )
            .prefetch_related("lines")
            .order_by("-created_at")
        )

    @staticmethod
    def get_snapshot_for_order(
        *,
        website,
        special_order,
    ) -> SpecialOrderPricingSnapshot:
        return SpecialOrderPricingSnapshot.objects.get(
            website=website,
            special_order=special_order,
        )