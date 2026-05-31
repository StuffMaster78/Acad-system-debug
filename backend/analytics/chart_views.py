"""
Chart-ready analytics endpoints.

Each view returns a standardised shape that the frontend can pass directly
to ECharts without any transformation:

{
  "labels":  ["Jan 2026", "Feb 2026", ...],
  "series":  [{"name": "Revenue", "data": [52000, 64100, ...]}, ...],
  "summary": {
    "current":    {"label": "May 2026", "value": 84200},
    "previous":   {"label": "Apr 2026", "value": 71900},
    "change_pct": 17.1
  }
}
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, DecimalField, Q, Sum
from django.db.models.functions import TruncMonth, TruncQuarter
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

# ── helpers ───────────────────────────────────────────────────────────────────

def _month_label(d: date) -> str:
    return d.strftime("%b %Y")

def _quarter_label(d: date) -> str:
    q = (d.month - 1) // 3 + 1
    return f"Q{q} {d.year}"

def _pct_change(current: float, previous: float) -> float | None:
    if not previous:
        return None
    return round((current - previous) / previous * 100, 1)

def _website_filter(request):
    """Return a Q() filter for website scoping."""
    website_id = request.query_params.get("website_id")
    if website_id:
        return Q(website_id=website_id)
    website = getattr(request, "website", None)
    if website:
        return Q(website=website)
    return Q()


# ── Revenue trend ─────────────────────────────────────────────────────────────

class RevenueTrendView(APIView):
    """
    GET /api/v1/analytics/charts/revenue/
    ?months=12   (default 12, max 36)
    ?period=month|quarter  (default month)
    ?website_id=  (superadmin multi-tenant filter)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from orders.models.orders import Order

        months = min(int(request.query_params.get("months", 12)), 36)
        period = request.query_params.get("period", "month")
        wf = _website_filter(request)

        start = (timezone.now() - timedelta(days=months * 31)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        trunc = TruncQuarter if period == "quarter" else TruncMonth
        label_fn = _quarter_label if period == "quarter" else _month_label

        rows = (
            Order.objects.filter(wf, is_paid=True, created_at__gte=start)
            .annotate(period=trunc("created_at"))
            .values("period")
            .annotate(
                revenue=Sum("total_price", output_field=DecimalField()),
                orders=Count("id"),
            )
            .order_by("period")
        )

        labels = [label_fn(r["period"].date()) for r in rows]
        revenue_data = [float(r["revenue"] or 0) for r in rows]
        orders_data = [r["orders"] for r in rows]

        summary = self._summary(revenue_data, labels)

        return Response(
            {
                "labels": labels,
                "series": [
                    {"name": "Revenue ($)", "data": revenue_data, "type": "line"},
                    {"name": "Orders", "data": orders_data, "type": "bar", "yAxisIndex": 1},
                ],
                "summary": summary,
            }
        )

    def _summary(self, data: list, labels: list) -> dict:
        if len(data) < 2:
            return {}
        return {
            "current": {"label": labels[-1], "value": data[-1]},
            "previous": {"label": labels[-2], "value": data[-2]},
            "change_pct": _pct_change(data[-1], data[-2]),
        }


# ── Orders by status ──────────────────────────────────────────────────────────

class OrdersTrendView(APIView):
    """
    GET /api/v1/analytics/charts/orders/
    ?months=12
    ?website_id=
    """

    permission_classes = [permissions.IsAuthenticated]

    TRACKED_STATUSES = [
        "pending", "assigned", "in_progress",
        "submitted", "completed", "cancelled",
    ]

    def get(self, request):
        from orders.models.orders import Order

        months = min(int(request.query_params.get("months", 12)), 36)
        wf = _website_filter(request)

        start = (timezone.now() - timedelta(days=months * 31)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        rows = (
            Order.objects.filter(wf, created_at__gte=start)
            .annotate(month=TruncMonth("created_at"))
            .values("month", "status")
            .annotate(count=Count("id"))
            .order_by("month", "status")
        )

        # Build month labels
        months_set: dict[str, dict[str, int]] = {}
        for r in rows:
            label = _month_label(r["month"].date())
            if label not in months_set:
                months_set[label] = {s: 0 for s in self.TRACKED_STATUSES}
            status = r["status"]
            if status in months_set[label]:
                months_set[label][status] += r["count"]

        labels = list(months_set.keys())

        series = [
            {
                "name": status.replace("_", " ").title(),
                "data": [months_set[lbl].get(status, 0) for lbl in labels],
                "type": "bar",
                "stack": "orders",
            }
            for status in self.TRACKED_STATUSES
        ]

        total_by_month = [sum(months_set[lbl].values()) for lbl in labels]
        summary = {}
        if len(total_by_month) >= 2:
            summary = {
                "current": {"label": labels[-1], "value": total_by_month[-1]},
                "previous": {"label": labels[-2], "value": total_by_month[-2]},
                "change_pct": _pct_change(total_by_month[-1], total_by_month[-2]),
            }

        return Response({"labels": labels, "series": series, "summary": summary})


# ── Client growth ─────────────────────────────────────────────────────────────

class ClientGrowthView(APIView):
    """
    GET /api/v1/analytics/charts/clients/
    ?months=12
    ?website_id=

    Returns new client registrations + cumulative active clients per month.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        months = min(int(request.query_params.get("months", 12)), 36)
        website_id = request.query_params.get("website_id")
        website = getattr(request, "website", None)

        start = (timezone.now() - timedelta(days=months * 31)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        qs = User.objects.filter(role="client", date_joined__gte=start)
        if website_id:
            qs = qs.filter(website_id=website_id)
        elif website:
            qs = qs.filter(website=website)

        rows = (
            qs.annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(new_clients=Count("id"))
            .order_by("month")
        )

        labels = [_month_label(r["month"].date()) for r in rows]
        new_data = [r["new_clients"] for r in rows]

        # Cumulative running total
        cumulative = []
        base = User.objects.filter(role="client", date_joined__lt=start)
        if website_id:
            base = base.filter(website_id=website_id)
        elif website:
            base = base.filter(website=website)
        running = base.count()
        for n in new_data:
            running += n
            cumulative.append(running)

        summary: dict = {}
        if len(new_data) >= 2:
            summary = {
                "current": {"label": labels[-1], "value": new_data[-1]},
                "previous": {"label": labels[-2], "value": new_data[-2]},
                "change_pct": _pct_change(new_data[-1], new_data[-2]),
            }

        return Response(
            {
                "labels": labels,
                "series": [
                    {"name": "New Clients", "data": new_data, "type": "bar"},
                    {"name": "Total Clients", "data": cumulative, "type": "line"},
                ],
                "summary": summary,
            }
        )


# ── Revenue by website (top N) ────────────────────────────────────────────────

class RevenueByWebsiteView(APIView):
    """
    GET /api/v1/analytics/charts/revenue-by-website/
    ?months=12&top=10

    Superadmin cross-tenant revenue comparison.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from orders.models.orders import Order
        from websites.models.websites import Website

        if getattr(request.user, "role", None) not in ("superadmin",) and not request.user.is_superuser:
            return Response({"detail": "Superadmin only."}, status=403)

        months = min(int(request.query_params.get("months", 12)), 36)
        top = min(int(request.query_params.get("top", 10)), 20)
        start = timezone.now() - timedelta(days=months * 31)

        rows = (
            Order.objects.filter(is_paid=True, created_at__gte=start, website__isnull=False)
            .values("website_id")
            .annotate(revenue=Sum("total_price", output_field=DecimalField()), orders=Count("id"))
            .order_by("-revenue")[:top]
        )

        website_ids = [r["website_id"] for r in rows]
        names = {w.id: w.name for w in Website.objects.filter(id__in=website_ids)}

        labels = [names.get(r["website_id"], f"Site #{r['website_id']}") for r in rows]
        revenue_data = [float(r["revenue"] or 0) for r in rows]
        orders_data = [r["orders"] for r in rows]

        return Response(
            {
                "labels": labels,
                "series": [
                    {"name": "Revenue ($)", "data": revenue_data, "type": "bar"},
                    {"name": "Orders", "data": orders_data, "type": "bar"},
                ],
                "summary": {},
            }
        )
