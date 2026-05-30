from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, Max, Min, Sum
from django.utils import timezone


class ClientAnalyticsService:
    """
    Analytics aggregations for a single client profile.

    All methods are read-only and safe to call from dashboard and
    reporting views. Each method returns a plain dict so callers can
    serialize however they need.
    """

    def __init__(self, *, client, days: int = 90):
        self.client = client
        self.days = days
        self.since = timezone.now() - timedelta(days=days)

    # ------------------------------------------------------------------
    # Spending
    # ------------------------------------------------------------------

    def get_spending_summary(self) -> dict[str, Any]:
        """Total spend, average order value, and largest single order."""
        qs = self._orders()
        agg = qs.aggregate(
            total=Sum("total_price"),
            avg=Avg("total_price"),
            max_order=Max("total_price"),
            min_order=Min("total_price"),
            count=Count("id"),
        )
        return {
            "total_spent": str(agg["total"] or Decimal("0.00")),
            "average_order_value": str(
                (agg["avg"] or Decimal("0.00")).quantize(Decimal("0.01"))
            ),
            "largest_order": str(agg["max_order"] or Decimal("0.00")),
            "smallest_order": str(agg["min_order"] or Decimal("0.00")),
            "total_orders": agg["count"] or 0,
            "period_days": self.days,
        }

    def get_spending_trend(self, *, buckets: int = 6) -> list[dict]:
        """
        Divide the analytics window into equal buckets and return
        spend + order count per bucket.

        Args:
            buckets: Number of time buckets (default 6 — bi-weekly for 90 days).

        Returns:
            List of dicts ordered oldest → newest, each with:
            period_start, period_end, total_spent, order_count.
        """
        bucket_size = timedelta(days=self.days // buckets)
        results = []
        cursor = self.since

        for _ in range(buckets):
            end = cursor + bucket_size
            agg = (
                self._orders()
                .filter(created_at__gte=cursor, created_at__lt=end)
                .aggregate(total=Sum("total_price"), count=Count("id"))
            )
            results.append({
                "period_start": cursor.date().isoformat(),
                "period_end": end.date().isoformat(),
                "total_spent": str(agg["total"] or Decimal("0.00")),
                "order_count": agg["count"] or 0,
            })
            cursor = end

        return results

    # ------------------------------------------------------------------
    # Order history
    # ------------------------------------------------------------------

    def get_order_status_breakdown(self) -> dict[str, int]:
        """Order counts grouped by status for the analytics window."""
        rows = (
            self._orders()
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        return {row["status"]: row["count"] for row in rows}

    def get_repeat_order_rate(self) -> dict[str, Any]:
        """
        Percentage of orders that are repeat orders (client has more than
        one order on the website).
        """
        total = self._orders().count()
        if total == 0:
            return {"total_orders": 0, "repeat_rate_percent": 0.0}

        # A client with more than 1 order is considered a repeat buyer.
        repeat = max(0, total - 1)
        return {
            "total_orders": total,
            "repeat_orders": repeat,
            "repeat_rate_percent": round((repeat / total) * 100, 1),
        }

    # ------------------------------------------------------------------
    # Loyalty & tier
    # ------------------------------------------------------------------

    def get_tier_progression(self) -> dict[str, Any]:
        """
        Current tier, points, and how far the client is from the next tier.
        """
        try:
            from loyalty_management.models import LoyaltyTier
        except ImportError:
            return {"tier": None, "points": 0, "next_tier": None}

        current_points = getattr(self.client, "loyalty_points", 0)
        current_tier = getattr(self.client, "tier", None)

        tiers = list(
            LoyaltyTier.objects.filter(
                website=self.client.website
            ).order_by("points_threshold")
        )

        next_tier = None
        points_to_next = None
        for tier in tiers:
            if tier.points_threshold > current_points:
                next_tier = tier.name
                points_to_next = tier.points_threshold - current_points
                break

        return {
            "current_tier": getattr(current_tier, "name", None),
            "current_points": current_points,
            "next_tier": next_tier,
            "points_to_next_tier": points_to_next,
        }

    def get_loyalty_transaction_summary(self) -> dict[str, Any]:
        """Earned vs redeemed loyalty points in the analytics window."""
        try:
            from loyalty_management.models import LoyaltyTransaction
        except ImportError:
            return {"earned": 0, "redeemed": 0, "net": 0}

        qs = LoyaltyTransaction.objects.filter(
            client=self.client,
            timestamp__gte=self.since,
        )
        earned = (
            qs.filter(points__gt=0).aggregate(total=Sum("points"))["total"] or 0
        )
        redeemed = abs(
            qs.filter(points__lt=0).aggregate(total=Sum("points"))["total"] or 0
        )
        return {
            "earned": earned,
            "redeemed": redeemed,
            "net": earned - redeemed,
            "period_days": self.days,
        }

    # ------------------------------------------------------------------
    # Disputes & issues
    # ------------------------------------------------------------------

    def get_dispute_summary(self) -> dict[str, Any]:
        """Dispute count and win/loss breakdown for the analytics window."""
        try:
            from orders.models import OrderDispute
        except ImportError:
            return {"total": 0}

        qs = OrderDispute.objects.filter(
            order__client=self.client.user,
            order__website=self.client.website,
            created_at__gte=self.since,
        )
        total = qs.count()
        if total == 0:
            return {"total": 0, "resolved_for_client": 0, "resolved_for_writer": 0}

        resolved_client = qs.filter(
            resolution__icontains="client"
        ).count()

        return {
            "total": total,
            "resolved_for_client": resolved_client,
            "resolved_for_writer": total - resolved_client,
            "period_days": self.days,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _orders(self):
        try:
            from orders.models import Order
        except ImportError:
            from django.db.models import QuerySet
            return QuerySet().none()

        return Order.objects.filter(
            client=self.client.user,
            website=self.client.website,
            created_at__gte=self.since,
        )
