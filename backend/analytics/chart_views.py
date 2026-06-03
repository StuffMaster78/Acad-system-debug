"""
Chart-ready analytics endpoints.

Each view returns a standardised shape that the frontend can pass directly
to ECharts without any transformation:

{
  "labels": ["Jan 2026", "Feb 2026", ...],
  "series": [{"name": "Revenue", "data": [52000, 64100, ...]}, ...],
  "summary": {
    "current": {"label": "May 2026", "value": 84200},
    "previous": {"label": "Apr 2026", "value": 71900},
    "change_pct": 17.1
  }
}
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from math import ceil

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


class IsClientOrStaff(permissions.BasePermission):
    """Allow clients to read their own chart data while staff retain tenant-scoped access."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", None)
        return role == "client" or role in _STAFF_ROLES or getattr(request.user, "is_superuser", False)


class IsWriterOrStaff(permissions.BasePermission):
    """Allow writers to read their own chart data while staff retain tenant-scoped access."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", None)
        return role == "writer" or role in _STAFF_ROLES or getattr(request.user, "is_superuser", False)


# ── helpers ───────────────────────────────────────────────────────────────────

def _month_label(d: date) -> str:
    return d.strftime("%b %Y")

def _quarter_label(d: date) -> str:
    q = (d.month - 1) // 3 + 1
    return f"Q{q} {d.year}"

def _safe_int(value, default: int, *, minimum: int = 1, maximum: int = 36) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))

def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)

def _month_start(d: date) -> date:
    return date(d.year, d.month, 1)

def _quarter_start(d: date) -> date:
    month = ((d.month - 1) // 3) * 3 + 1
    return date(d.year, month, 1)

def _as_aware_start(d: date):
    return timezone.make_aware(
        datetime.combine(d, time.min),
        timezone.get_current_timezone(),
    )

def _period_buckets(*, months: int, period: str = "month") -> tuple[list[date], object]:
    today = timezone.localdate()
    if period == "quarter":
        count = max(1, ceil(months / 3))
        current = _quarter_start(today)
        buckets = [_add_months(current, (idx - count + 1) * 3) for idx in range(count)]
    else:
        current = _month_start(today)
        buckets = [_add_months(current, idx - months + 1) for idx in range(months)]
    return buckets, _as_aware_start(buckets[0])

def _chart_summary(data: list[float | int], labels: list[str]) -> dict:
    if len(data) < 2:
        return {}
    return {
        "current": {"label": labels[-1], "value": data[-1]},
        "previous": {"label": labels[-2], "value": data[-2]},
        "change_pct": _pct_change(float(data[-1]), float(data[-2])),
    }

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
    ?months=12 (default 12, max 36)
    ?period=month|quarter (default month)
    ?website_id= (superadmin multi-tenant filter)
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from orders.models.orders import Order

        months = _safe_int(request.query_params.get("months"), 12, maximum=36)
        period = request.query_params.get("period", "month")
        if period not in {"month", "quarter"}:
            period = "month"
        wf = _website_filter(request)
        buckets, start = _period_buckets(months=months, period=period)

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

        row_map = {label_fn(r["period"].date()): r for r in rows}
        labels = [label_fn(bucket) for bucket in buckets]
        revenue_data = [float((row_map.get(label) or {}).get("revenue") or 0) for label in labels]
        orders_data = [int((row_map.get(label) or {}).get("orders") or 0) for label in labels]
        summary = _chart_summary(revenue_data, labels)

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

        months = _safe_int(request.query_params.get("months"), 12, maximum=36)
        wf = _website_filter(request)
        buckets, start = _period_buckets(months=months)

        rows = (
            Order.objects.filter(wf, created_at__gte=start)
            .annotate(month=TruncMonth("created_at"))
            .values("month", "status")
            .annotate(count=Count("id"))
            .order_by("month", "status")
        )

        labels = [_month_label(bucket) for bucket in buckets]
        months_set: dict[str, dict[str, int]] = {
            label: {s: 0 for s in self.TRACKED_STATUSES}
            for label in labels
        }
        for r in rows:
            label = _month_label(r["month"].date())
            status = r["status"]
            if label in months_set and status in months_set[label]:
                months_set[label][status] += r["count"]

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
        summary = _chart_summary(total_by_month, labels)

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
        months = _safe_int(request.query_params.get("months"), 12, maximum=36)
        wf = _website_filter(request)
        buckets, start = _period_buckets(months=months)

        qs = User.objects.filter(wf, role="client", date_joined__gte=start)

        rows = (
            qs.annotate(month=TruncMonth("date_joined"))
            .values("month")
            .annotate(new_clients=Count("id"))
            .order_by("month")
        )

        row_map = {_month_label(r["month"].date()): r["new_clients"] for r in rows}
        labels = [_month_label(bucket) for bucket in buckets]
        new_data = [int(row_map.get(label, 0)) for label in labels]

        # Cumulative running total
        cumulative = []
        base = User.objects.filter(wf, role="client", date_joined__lt=start)
        running = base.count()
        for n in new_data:
            running += n
            cumulative.append(running)

        summary = _chart_summary(new_data, labels)

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
    ?days=14 (default 14, max 30)
    ?website_id=

    Last N days of daily revenue + order count — used for the sidebar sparkline.
    Returns lightweight data: labels are short day strings, two series.
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from orders.models.orders import Order
        from django.db.models.functions import TruncDay

        days = _safe_int(request.query_params.get("days"), 14, maximum=30)
        wf = _website_filter(request)
        today = timezone.localdate()
        buckets = [today - timedelta(days=idx) for idx in range(days - 1, -1, -1)]
        start = _as_aware_start(buckets[0])

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

        row_map = {r["day"].date(): r for r in rows}
        labels = [f"{bucket.day} {bucket:%b}" for bucket in buckets]
        revenue_data = [float((row_map.get(bucket) or {}).get("revenue") or 0) for bucket in buckets]
        orders_data = [int((row_map.get(bucket) or {}).get("orders") or 0) for bucket in buckets]

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
    ?metric=revenue|orders|clients (default revenue)
    ?compare=mom|qoq|yoy (default mom)
    ?website_id=

    Returns current period vs previous period side-by-side with growth %.
    MoM = current month vs prior month
    QoQ = current quarter vs prior quarter
    YoY = current year vs prior year
    """

    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from orders.models.orders import Order

        metric = request.query_params.get("metric", "revenue")
        if metric not in {"revenue", "orders", "clients"}:
            metric = "revenue"
        compare = request.query_params.get("compare", "mom")
        if compare not in {"mom", "qoq", "yoy"}:
            compare = "mom"
        wf = _website_filter(request)
        now = timezone.now()

        # Determine date ranges
        if compare == "yoy":
            cur_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            cur_end = now
            prev_start = cur_start.replace(year=cur_start.year - 1)
            prev_end = cur_end.replace(year=cur_end.year - 1)
            label_cur = str(now.year)
            label_prev = str(now.year - 1)
        elif compare == "qoq":
            q = (now.month - 1) // 3
            cur_start = now.replace(month=q * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            cur_end = now
            prev_month = (q - 1) * 3 + 1 if q > 0 else 10
            prev_year = now.year if q > 0 else now.year - 1
            prev_start = now.replace(year=prev_year, month=prev_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            prev_end = cur_start
            label_cur = f"Q{q + 1} {now.year}"
            label_prev = f"Q{q} {prev_year}" if q > 0 else f"Q4 {now.year - 1}"
        else: # mom
            cur_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cur_end = now
            prev_end = cur_start
            prev_start = (cur_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            label_cur = cur_start.strftime("%b %Y")
            label_prev = prev_start.strftime("%b %Y")

        if metric == "clients":
            cur_val = User.objects.filter(
                wf,
                role="client",
                date_joined__gte=cur_start,
                date_joined__lt=cur_end,
            ).count()
            prev_val = User.objects.filter(
                wf,
                role="client",
                date_joined__gte=prev_start,
                date_joined__lt=prev_end,
            ).count()
        elif metric == "orders":
            cur_val = Order.objects.filter(
                wf,
                created_at__gte=cur_start,
                created_at__lt=cur_end,
            ).count()
            prev_val = Order.objects.filter(
                wf,
                created_at__gte=prev_start,
                created_at__lt=prev_end,
            ).count()
        else: # revenue
            cur_val = float(Order.objects.filter(
                wf,
                payment_status='paid',
                created_at__gte=cur_start,
                created_at__lt=cur_end,
            ).aggregate(v=Sum("total_price", output_field=DecimalField()))["v"] or 0)
            prev_val = float(Order.objects.filter(
                wf,
                payment_status='paid',
                created_at__gte=prev_start,
                created_at__lt=prev_end,
            ).aggregate(v=Sum("total_price", output_field=DecimalField()))["v"] or 0)

        return Response({
            "metric": metric,
            "compare": compare,
            "current": {"label": label_cur, "value": cur_val},
            "previous": {"label": label_prev, "value": prev_val},
            "change_pct": _pct_change(float(cur_val), float(prev_val)),
            "labels": [label_prev, label_cur],
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

    permission_classes = [IsWriterOrStaff]

    def get(self, request):
        from wallets.models import WalletEntry

        months = _safe_int(request.query_params.get("months"), 12, maximum=36)
        buckets, start = _period_buckets(months=months)

        rows = (
            WalletEntry.objects.filter(
                wallet__owner_user=request.user,
                direction="credit",
                created_at__gte=start,
            )
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(earnings=Sum("amount", output_field=DecimalField()), events=Count("id"))
            .order_by("month")
        )

        row_map = {_month_label(r["month"].date()): r for r in rows}
        labels = [_month_label(bucket) for bucket in buckets]
        earnings_data = [float((row_map.get(label) or {}).get("earnings") or 0) for label in labels]
        events_data = [int((row_map.get(label) or {}).get("events") or 0) for label in labels]

        summary = _chart_summary(earnings_data, labels)

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

    permission_classes = [IsClientOrStaff]

    def get(self, request):
        from orders.models.orders import Order

        months = _safe_int(request.query_params.get("months"), 12, maximum=36)
        buckets, start = _period_buckets(months=months)

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

        row_map = {_month_label(r["month"].date()): r for r in rows}
        labels = [_month_label(bucket) for bucket in buckets]
        spend_data = [float((row_map.get(label) or {}).get("spend") or 0) for label in labels]
        orders_data = [int((row_map.get(label) or {}).get("orders") or 0) for label in labels]

        summary = _chart_summary(spend_data, labels)

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

        months = _safe_int(request.query_params.get("months"), 12, maximum=36)
        top = _safe_int(request.query_params.get("top"), 10, maximum=20)
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


class ClientOrderSummaryView(APIView):
    """
    GET /api/v1/analytics/charts/client-summary/

    Returns lifetime order summary and the 5 most recent paid orders
    for the authenticated client.  Intended for the client spending
    dashboard to show totals and a recent-orders row alongside charts.
    """

    permission_classes = [IsClientOrStaff]

    def get(self, request):
        from orders.models.orders import Order

        qs = Order.objects.filter(
            client=request.user,
            payment_status="paid",
        ).order_by("-created_at")

        agg = qs.aggregate(
            total_spend=Sum("total_price", output_field=DecimalField()),
            total_orders=Count("id"),
        )
        total_spend = float(agg["total_spend"] or 0)
        total_orders = agg["total_orders"] or 0
        avg_order = round(total_spend / total_orders, 2) if total_orders else 0.0

        recent = qs[:5].values(
            "id", "topic", "total_price", "currency", "status", "created_at",
        )
        recent_list = [
            {
                "id": r["id"],
                "topic": r["topic"] or "",
                "amount": float(r["total_price"] or 0),
                "currency": r["currency"] or "USD",
                "status": r["status"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in recent
        ]

        return Response(
            {
                "total_spend": total_spend,
                "total_orders": total_orders,
                "avg_order_value": avg_order,
                "recent_orders": recent_list,
            }
        )
