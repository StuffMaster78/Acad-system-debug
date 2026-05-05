from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from discounts.selectors.discount_selectors import DiscountSelector
from discounts.selectors.discount_usage_selectors import (
    DiscountUsageSelector,
)


class DiscountDashboardSelector:
    """
    Dashboard read queries for discount analytics.
    """

    @staticmethod
    def get_summary(*, website) -> dict:
        """
        Return high-level dashboard totals.
        """
        discounts = DiscountSelector.base_queryset(website=website)
        usages = DiscountUsageSelector.base_queryset(website=website)

        usage_totals = usages.aggregate(
            total_redemptions=Count("id"),
            total_discount_given=Coalesce(
                Sum("discount_amount"),
                Decimal("0.00"),
            ),
            distinct_clients=Count("client", distinct=True),
        )

        return {
            "total_discounts": discounts.count(),
            "working_discounts": (
                DiscountSelector.list_working(website=website).count()
            ),
            "scheduled_discounts": (
                DiscountSelector.list_scheduled(website=website).count()
            ),
            "expired_discounts": (
                DiscountSelector.list_expired(website=website).count()
            ),
            "archived_discounts": (
                DiscountSelector.list_archived(website=website).count()
            ),
            "total_redemptions": usage_totals["total_redemptions"],
            "total_discount_given": usage_totals["total_discount_given"],
            "distinct_clients": usage_totals["distinct_clients"],
        }

    @staticmethod
    def list_expiring_soon(
        *,
        website,
        days: int = 7,
    ):
        """
        Return active discounts expiring within the given number of days.
        """
        days = max(days, 1)

        now = timezone.now()
        cutoff = now + timedelta(days=days)

        return DiscountSelector.list_working(website=website).filter(
            ends_at__isnull=False,
            ends_at__gte=now,
            ends_at__lte=cutoff,
        )

    @staticmethod
    def list_top_performing(*, website, limit: int = 10):
        """
        Return discounts ordered by usage count and discount amount.
        """
        limit = max(limit, 1)

        return (
            DiscountSelector.base_queryset(website=website)
            .annotate(
                usage_count=Count("usages", distinct=True),
                total_discount_given=Coalesce(
                    Sum("usages__discount_amount"),
                    Decimal("0.00"),
                ),
                distinct_clients=Count(
                    "usages__client",
                    distinct=True,
                ),
            )
            .order_by("-usage_count", "-total_discount_given")[:limit]
        )

    @staticmethod
    def list_unused_working(*, website):
        """
        Return active discounts that have not been used.
        """
        return (
            DiscountSelector.list_working(website=website)
            .annotate(usage_count=Count("usages", distinct=True))
            .filter(usage_count=0)
        )

    @staticmethod
    def group_by_origin(*, website):
        """
        Return discount counts grouped by origin.
        """
        return (
            DiscountSelector.base_queryset(website=website)
            .values("origin")
            .annotate(total=Count("id", distinct=True))
            .order_by("origin")
        )