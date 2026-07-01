"""
Platform profit summary endpoint.

Computes gross revenue, expenditure breakdown, and net profit for a given
time slice (settlement cycle, calendar month, quarter, or year).

GET /api/v1/ledger/profit-summary/
    ?period=month          # month | quarter | year | cycle
    &website_id=3          # optional; omit for platform-wide total
    &year=2026
    &month=7               # only for period=month
    &quarter=2             # only for period=quarter
    &cycle_id=45           # only for period=cycle

Response:
{
  "period_label": "July 2026",
  "website_id": 3,
  "revenue": {
    "gross_client_payments": "18500.00",
    "refunds_issued": "-320.00",
    "wallet_credits_issued": "-45.00",
    "net_revenue": "18135.00"
  },
  "expenditure": {
    "writer_payouts": "12400.00",
    "writer_bonuses": "320.00",
    "writer_tips": "180.00",
    "writer_fines_recovered": "-95.00",
    "total_expenditure": "12805.00"
  },
  "profit": "5330.00",
  "margin_pct": "29.39"
}
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.constants import EntrySide, LedgerEntryType
from ledger.models import JournalLine


def _zero() -> Decimal:
    return Decimal("0.00")


def _sum_lines(qs) -> Decimal:
    result = qs.aggregate(total=Sum("amount"))["total"]
    return Decimal(str(result)) if result is not None else _zero()


def _date_range(period: str, year: int, month: int, quarter: int, cycle_id: int | None):
    """Return (start, end) inclusive dates for the requested period."""
    if period == "month":
        start = date(year, month, 1)
        # Last day of month
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
        label = start.strftime("%B %Y")

    elif period == "quarter":
        q_month = (quarter - 1) * 3 + 1
        start = date(year, q_month, 1)
        end_month = q_month + 3
        if end_month > 12:
            end = date(year + 1, end_month - 12, 1) - timedelta(days=1)
        else:
            end = date(year, end_month, 1) - timedelta(days=1)
        label = f"Q{quarter} {year}"

    elif period == "year":
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        label = str(year)

    elif period == "cycle" and cycle_id:
        from writer_compensation.models.payment_window import PaymentWindow
        try:
            win = PaymentWindow.objects.get(pk=cycle_id)
            start = win.start_date
            end = win.end_date
            label = win.title or f"Cycle #{cycle_id}"
        except PaymentWindow.DoesNotExist:
            start = date.today().replace(day=1)
            end = date.today()
            label = f"Cycle #{cycle_id} (not found)"

    else:
        # Default: current month
        today = date.today()
        start = today.replace(day=1)
        end = today
        label = today.strftime("%B %Y")

    return start, end, label


class PlatformProfitSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        # ── Auth guard ────────────────────────────────────────────────────────
        if request.user.role not in ("admin", "superadmin"):
            from rest_framework import status
            return Response(
                {"detail": "Admin or superadmin access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # ── Parameters ────────────────────────────────────────────────────────
        period   = request.query_params.get("period", "month")
        website_id = request.query_params.get("website_id")
        year     = int(request.query_params.get("year", date.today().year))
        month    = int(request.query_params.get("month", date.today().month))
        quarter  = int(request.query_params.get("quarter", (date.today().month - 1) // 3 + 1))
        cycle_id = request.query_params.get("cycle_id")
        if cycle_id:
            cycle_id = int(cycle_id)

        start, end, label = _date_range(period, year, month, quarter, cycle_id)

        # ── Base querysets ────────────────────────────────────────────────────
        date_filter = Q(
            journal_entry__created_at__date__gte=start,
            journal_entry__created_at__date__lte=end,
        )
        if website_id:
            date_filter &= Q(journal_entry__website_id=int(website_id))

        lines = JournalLine.objects.filter(date_filter)

        def revenue_lines(*types):
            return lines.filter(
                entry_type__in=types,
                entry_side=EntrySide.CREDIT,
            )

        def expense_lines(*types):
            return lines.filter(
                entry_type__in=types,
                entry_side=EntrySide.DEBIT,
            )

        # ── Revenue ───────────────────────────────────────────────────────────
        gross_payments = _sum_lines(
            lines.filter(
                entry_type__in=[
                    LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE,
                    LedgerEntryType.ORDER_PAYMENT,
                    LedgerEntryType.CLIENT_WALLET_TOP_UP,
                    LedgerEntryType.ORDER_INSTALLMENT_PAYMENT,
                    LedgerEntryType.SPECIAL_ORDER_DEPOSIT,
                    LedgerEntryType.SPECIAL_ORDER_INSTALLMENT,
                    LedgerEntryType.CLASS_PAYMENT,
                ],
                entry_side=EntrySide.CREDIT,
            )
        )

        refunds_issued = _sum_lines(
            lines.filter(
                entry_type__in=[
                    LedgerEntryType.EXTERNAL_REFUND,
                ],
                entry_side=EntrySide.DEBIT,
            )
        )

        wallet_credits = _sum_lines(
            lines.filter(
                entry_type__in=[
                    LedgerEntryType.CLIENT_WALLET_SUPPORT_CREDIT,
                ],
                entry_side=EntrySide.CREDIT,
            )
        )

        net_revenue = gross_payments - refunds_issued - wallet_credits

        # ── Expenditure ───────────────────────────────────────────────────────
        writer_payouts = _sum_lines(
            lines.filter(
                entry_type=LedgerEntryType.WRITER_PAYOUT,
                entry_side=EntrySide.DEBIT,
            )
        )

        writer_bonuses = _sum_lines(
            lines.filter(
                entry_type=LedgerEntryType.WRITER_BONUS,
                entry_side=EntrySide.DEBIT,
            )
        )

        writer_tips = _sum_lines(
            lines.filter(
                entry_type=LedgerEntryType.TIP_SETTLEMENT,
                entry_side=EntrySide.DEBIT,
            )
        )

        fines_recovered = _sum_lines(
            lines.filter(
                entry_type=LedgerEntryType.WRITER_FINE,
                entry_side=EntrySide.CREDIT,
            )
        )

        total_expenditure = writer_payouts + writer_bonuses + writer_tips - fines_recovered

        # ── Profit ────────────────────────────────────────────────────────────
        profit = net_revenue - total_expenditure
        margin_pct = (
            (profit / net_revenue * 100).quantize(Decimal("0.01"))
            if net_revenue > 0
            else _zero()
        )

        return Response({
            "period_label": label,
            "period": period,
            "date_range": {"from": str(start), "to": str(end)},
            "website_id": website_id,
            "revenue": {
                "gross_client_payments": str(gross_payments.quantize(Decimal("0.01"))),
                "refunds_issued": str(refunds_issued.quantize(Decimal("0.01"))),
                "wallet_credits_issued": str(wallet_credits.quantize(Decimal("0.01"))),
                "net_revenue": str(net_revenue.quantize(Decimal("0.01"))),
            },
            "expenditure": {
                "writer_payouts": str(writer_payouts.quantize(Decimal("0.01"))),
                "writer_bonuses": str(writer_bonuses.quantize(Decimal("0.01"))),
                "writer_tips": str(writer_tips.quantize(Decimal("0.01"))),
                "fines_recovered": str(fines_recovered.quantize(Decimal("0.01"))),
                "total_expenditure": str(total_expenditure.quantize(Decimal("0.01"))),
            },
            "profit": str(profit.quantize(Decimal("0.01"))),
            "margin_pct": str(margin_pct),
        })
