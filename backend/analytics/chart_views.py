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

_STAFF_ROLES = {"superadmin", "admin", "support", "editor"}


class IsStaffOrAdmin(permissions.BasePermission):
    """Restrict analytics endpoints to staff roles (admin, support, editor, superadmin)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", None)
        return role in _STAFF_ROLES or getattr(request.user, "is_superuser", False)


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
    """
    Return a Q() filter for website scoping.

    Security: only superadmin may see cross-tenant data (no website filter).
    All other roles are scoped to their resolved website, then to their user
    website as a fallback. Non-staff roles (writer, client) get an impossible
    Q that returns no rows.
    """
    user = request.user
    role = getattr(user, "role", None)
    is_super = role == "superadmin" or getattr(user, "is_superuser", False)

    website_id = request.query_params.get("website_id")
    if website_id and is_super:
        return Q(website_id=website_id)

    website = getattr(request, "website", None) or getattr(user, "website", None)
    if website:
        return Q(website=website)

    # Superadmin without a specific website_id or resolved website → all tenants.
    if is_super:
        return Q()

    # Any other role with no resolvable website: deny all rows.
    return Q(pk__isnull=True)


# ── Revenue trend ─────────────────────────────────────────────────────────────

class RevenueTrendView(APIView):
    """
    GET /api/v1/analytics/charts/revenue/
    ?months=12   (default 12, max 36)
    ?period=month|quarter  (default month)
    ?website_id=  (superadmin multi-tenant filter)
    """

    permission_classes = [IsStaffOrAdmin]

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
            Order.objects.filter(wf, payment_status='paid', created_at__gte=start)
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

    permission_classes = [IsStaffOrAdmin]

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

    permission_classes = [IsStaffOrAdmin]

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

class DailySparklineView(APIView):
    """
    GET /api/v1/analytics/charts/daily/
    ?days=14   (default 14, max 30)
    ?website_id=

    Last N days of daily revenue + order count — used for the sidebar sparkline.
    Returns lightweight data: labels are short day strings, two series.
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from orders.models.orders import Order
        from django.db.models.functions import TruncDay

        days = min(int(request.query_params.get("days", 14)), 30)
        wf = _website_filter(request)
        start = timezone.now() - timedelta(days=days)

        rows = (
            Order.objects.filter(wf, payment_status='paid', created_at__gte=start)
            .annotate(day=TruncDay("created_at"))
            .values("day")
            .annotate(
                revenue=Sum("total_price", output_field=DecimalField()),
                orders=Count("id"),
            )
            .order_by("day")
        )

        labels = [r["day"].strftime("%-d %b") for r in rows]
        revenue_data = [float(r["revenue"] or 0) for r in rows]
        orders_data = [r["orders"] for r in rows]

        total_revenue = sum(revenue_data)
        total_orders = sum(orders_data)

        return Response({
            "labels": labels,
            "series": [
                {"name": "Revenue", "data": revenue_data, "type": "line"},
                {"name": "Orders", "data": orders_data, "type": "line"},
            ],
            "summary": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "days": days,
            },
        })


class PeriodComparisonView(APIView):
    """
    GET /api/v1/analytics/charts/comparison/
    ?metric=revenue|orders|clients  (default revenue)
    ?compare=mom|qoq|yoy            (default mom)
    ?website_id=

    Returns current period vs previous period side-by-side with growth %.
    MoM = current month vs prior month
    QoQ = current quarter vs prior quarter
    YoY = current year vs prior year
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from orders.models.orders import Order

        metric  = request.query_params.get("metric", "revenue")
        compare = request.query_params.get("compare", "mom")
        wf      = _website_filter(request)
        now     = timezone.now()

        # Determine date ranges
        if compare == "yoy":
            cur_start  = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            cur_end    = now
            prev_start = cur_start.replace(year=cur_start.year - 1)
            prev_end   = cur_end.replace(year=cur_end.year - 1)
            label_cur  = str(now.year)
            label_prev = str(now.year - 1)
        elif compare == "qoq":
            q = (now.month - 1) // 3
            cur_start  = now.replace(month=q * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            cur_end    = now
            prev_month = (q - 1) * 3 + 1 if q > 0 else 10
            prev_year  = now.year if q > 0 else now.year - 1
            prev_start = now.replace(year=prev_year, month=prev_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            prev_end   = cur_start
            label_cur  = f"Q{q + 1} {now.year}"
            label_prev = f"Q{q} {prev_year}" if q > 0 else f"Q4 {now.year - 1}"
        else:  # mom
            cur_start  = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cur_end    = now
            prev_end   = cur_start
            prev_start = (cur_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            label_cur  = cur_start.strftime("%b %Y")
            label_prev = prev_start.strftime("%b %Y")

        if metric == "clients":
            cur_val  = User.objects.filter(role="client", date_joined__gte=cur_start, date_joined__lte=cur_end).count()
            prev_val = User.objects.filter(role="client", date_joined__gte=prev_start, date_joined__lte=prev_end).count()
        elif metric == "orders":
            cur_val  = Order.objects.filter(wf, created_at__gte=cur_start, created_at__lte=cur_end).count()
            prev_val = Order.objects.filter(wf, created_at__gte=prev_start, created_at__lte=prev_end).count()
        else:  # revenue
            from django.db.models import Sum, DecimalField
            cur_val  = float(Order.objects.filter(wf, payment_status='paid', created_at__gte=cur_start, created_at__lte=cur_end).aggregate(v=Sum("total_price", output_field=DecimalField()))["v"] or 0)
            prev_val = float(Order.objects.filter(wf, payment_status='paid', created_at__gte=prev_start, created_at__lte=prev_end).aggregate(v=Sum("total_price", output_field=DecimalField()))["v"] or 0)

        return Response({
            "metric": metric,
            "compare": compare,
            "current":  {"label": label_cur,  "value": cur_val},
            "previous": {"label": label_prev, "value": prev_val},
            "change_pct": _pct_change(float(cur_val), float(prev_val)),
            "labels":  [label_prev, label_cur],
            "series": [{
                "name": metric.title(),
                "data": [prev_val, cur_val],
                "type": "bar",
            }],
        })


class WriterEarningsTrendView(APIView):
    """
    GET /api/v1/analytics/charts/writer-earnings/
    ?months=12

    Writer's own earnings by month from wallet credit events.
    Scoped to the authenticated writer automatically.
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from wallets.models import Wallet

        months = min(int(request.query_params.get("months", 12)), 36)
        start = (timezone.now() - timedelta(days=months * 31)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        try:
            wallet = Wallet.objects.get(user=request.user)
            rows = (
                wallet.entries.filter(created_at__gte=start, direction="credit")
                .annotate(month=TruncMonth("created_at"))
                .values("month")
                .annotate(earnings=Sum("amount", output_field=DecimalField()), events=Count("id"))
                .order_by("month")
            )
        except Exception:
            rows = []

        labels = [_month_label(r["month"].date()) for r in rows]
        earnings_data = [float(r["earnings"] or 0) for r in rows]
        events_data = [r["events"] for r in rows]

        summary: dict = {}
        if len(earnings_data) >= 2:
            summary = {
                "current": {"label": labels[-1], "value": earnings_data[-1]},
                "previous": {"label": labels[-2], "value": earnings_data[-2]},
                "change_pct": _pct_change(earnings_data[-1], earnings_data[-2]),
            }

        return Response(
            {
                "labels": labels,
                "series": [
                    {"name": "Earnings ($)", "data": earnings_data, "type": "bar"},
                    {"name": "Events", "data": events_data, "type": "line", "yAxisIndex": 1},
                ],
                "summary": summary,
            }
        )


class ClientSpendingTrendView(APIView):
    """
    GET /api/v1/analytics/charts/client-spending/
    ?months=12

    Client's own paid orders by month — spend trend and order count.
    Scoped to the authenticated client automatically.
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from orders.models.orders import Order

        months = min(int(request.query_params.get("months", 12)), 36)
        start = (timezone.now() - timedelta(days=months * 31)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        rows = (
            Order.objects.filter(client=request.user, payment_status='paid', created_at__gte=start)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                spend=Sum("total_price", output_field=DecimalField()),
                orders=Count("id"),
            )
            .order_by("month")
        )

        labels = [_month_label(r["month"].date()) for r in rows]
        spend_data = [float(r["spend"] or 0) for r in rows]
        orders_data = [r["orders"] for r in rows]

        summary: dict = {}
        if len(spend_data) >= 2:
            summary = {
                "current": {"label": labels[-1], "value": spend_data[-1]},
                "previous": {"label": labels[-2], "value": spend_data[-2]},
                "change_pct": _pct_change(spend_data[-1], spend_data[-2]),
            }

        return Response(
            {
                "labels": labels,
                "series": [
                    {"name": "Spend ($)", "data": spend_data, "type": "bar"},
                    {"name": "Orders", "data": orders_data, "type": "line", "yAxisIndex": 1},
                ],
                "summary": summary,
            }
        )


class RevenueByWebsiteView(APIView):
    """
    GET /api/v1/analytics/charts/revenue-by-website/
    ?months=12&top=10

    Superadmin cross-tenant revenue comparison.
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from orders.models.orders import Order
        from websites.models.websites import Website

        if getattr(request.user, "role", None) not in ("superadmin",) and not request.user.is_superuser:
            return Response({"detail": "Superadmin only."}, status=403)

        months = min(int(request.query_params.get("months", 12)), 36)
        top = min(int(request.query_params.get("top", 10)), 20)
        start = timezone.now() - timedelta(days=months * 31)

        rows = (
            Order.objects.filter(payment_status='paid', created_at__gte=start, website__isnull=False)
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
