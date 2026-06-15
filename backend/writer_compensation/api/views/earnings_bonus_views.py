from __future__ import annotations

from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.permissions import IsAdminOrSuperAdmin
from writer_compensation.permissions.permissions import IsWriter
from writer_compensation.permissions.base import IsFinanceStaff
from writer_compensation.services.bonus_service import BonusService
from writer_compensation.services.earnings_query_service import EarningsQueryService
from writer_compensation.selectors.window_selectors import WindowSelectors


def _get_website(request):
    return request.website


def _get_writer_profile(request):
    return request.user.writer_profile


def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


# ===========================================================================
# ADMIN — Earnings
# ===========================================================================

class AdminWriterEarningsView(APIView):
    """
    GET /admin/writers/{writer_id}/earnings/
        ?from_date=2026-05-01&to_date=2026-05-14

    Period earnings totals for one writer.
    Broken down by base, bonus, tips, deductions, reversals, advances, net.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, writer_id):
        website = _get_website(request)
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if not from_date or not to_date:
            return _error("from_date and to_date query params are required.", 400)

        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        result = EarningsQueryService.get_period_totals(
            website=website,
            start_date=from_date,
            end_date=to_date,
            writer=writer,
        )
        return Response(result)


class AdminWriterEarningsBreakdownView(APIView):
    """
    GET /admin/writers/{writer_id}/earnings/breakdown/
        ?from_date=2026-05-01&to_date=2026-05-14

    Per-event-type subtotals for one writer in a date range.
    Useful for debugging mismatches and admin reporting.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, writer_id):
        website = _get_website(request)
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if not from_date or not to_date:
            return _error("from_date and to_date query params are required.", 400)

        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        result = EarningsQueryService.get_period_breakdown_by_event_type(
            website=website,
            writer=writer,
            start_date=from_date,
            end_date=to_date,
        )
        return Response(result)


class AdminWriterFullEarningsView(APIView):
    """
    GET /admin/writers/{writer_id}/earnings/full/
        ?window_id=12 (optional — omit for full history)

    Full earnings reconstruction grouped by window.
    Includes anomaly audit flags.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, writer_id):
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        window_id = request.query_params.get("window_id")
        window = None

        if window_id:
            website = _get_website(request)
            window = WindowSelectors.get_window_by_id(int(window_id), website)
            if not window:
                return _error("Window not found.", 404)

        result = EarningsQueryService.get_writer_earnings(
            writer=writer,
            window=window,
        )
        return Response(result)


class AdminWindowEarningsBreakdownView(APIView):
    """
    GET /admin/windows/{window_id}/earnings/

    All writers' earnings grouped by writer for a window.
    Powers the payout batch overview with per-writer nets.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, window_id):
        website = _get_website(request)
        window = WindowSelectors.get_window_by_id(window_id, website)
        if not window:
            return _error("Window not found.", 404)

        result = EarningsQueryService.get_window_breakdown(window)
        return Response(result)


# ===========================================================================
# ADMIN — Bonuses
# ===========================================================================

class AdminApplyMilestoneBonusView(APIView):
    """
    POST /admin/writers/{writer_id}/bonuses/milestone/
    Body: { "milestone": 100, "amount": "300.00" }

    Manually trigger a milestone bonus for a writer.
    Idempotent — safe to call multiple times for the same milestone.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, writer_id):
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        milestone = request.data.get("milestone")
        amount = request.data.get("amount")

        if not milestone or not amount:
            return _error("milestone and amount are required.", 400)

        try:
            milestone = int(milestone)
            amount = Decimal(str(amount))
        except Exception:
            return _error("milestone must be an integer, amount must be a decimal.", 400)

        event = BonusService.apply_milestone_bonus(
            writer=writer,
            milestone=milestone,
            amount=amount,
            website=_get_website(request),
            created_by=request.user,
        )

        if event is None:
            return Response(
                {"detail": f"Milestone {milestone} already awarded to this writer."},
                status=status.HTTP_200_OK,
            )

        from writer_compensation.api.serializers.compensation_event_serializers import (
            CompensationEventSerializer,
        )
        return Response(
            CompensationEventSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )


class AdminApplyPerformanceBonusView(APIView):
    """
    POST /admin/writers/{writer_id}/bonuses/performance/
    Body: { "order_id": 4821, "base_amount": "120.00" }

    Manually trigger a performance bonus calculation and application
    for a completed order.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, writer_id):
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        order_id = request.data.get("order_id")
        base_amount = request.data.get("base_amount")

        if not order_id or not base_amount:
            return _error("order_id and base_amount are required.", 400)

        from orders.models.orders import Order
        try:
            order = Order.objects.get(pk=order_id)
            base_amount = Decimal(str(base_amount))
        except Order.DoesNotExist:
            return _error("Order not found.", 404)
        except Exception:
            return _error("Invalid base_amount.", 400)

        event = BonusService.apply_performance_bonus(
            writer=writer,
            order=order,
            base_amount=base_amount,
            website=_get_website(request),
            created_by=request.user,
        )

        if event is None:
            return Response(
                {"detail": "Writer does not qualify for a performance bonus on this order."},
                status=status.HTTP_200_OK,
            )

        from writer_compensation.api.serializers.compensation_event_serializers import (
            CompensationEventSerializer,
        )
        return Response(
            CompensationEventSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )


class AdminApplyRetentionBonusView(APIView):
    """
    POST /admin/writers/{writer_id}/bonuses/retention/

    Apply a retention bonus for the current month if the writer qualifies.
    Idempotent — the monthly idempotency key prevents double awards.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, writer_id):
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        event = BonusService.apply_retention_bonus(
            writer=writer,
            website=_get_website(request),
            created_by=request.user,
        )

        if event is None:
            return Response(
                {"detail": "Writer does not qualify for a retention bonus this period."},
                status=status.HTTP_200_OK,
            )

        from writer_compensation.api.serializers.compensation_event_serializers import (
            CompensationEventSerializer,
        )
        return Response(
            CompensationEventSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )


class AdminWriterBonusHistoryView(APIView):
    """
    GET /admin/writers/{writer_id}/bonuses/
        ?limit=50

    Full bonus event history for a writer.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, writer_id):
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        limit = int(request.query_params.get("limit", 50))
        events = BonusService.get_bonus_history(writer=writer, limit=limit)

        from writer_compensation.api.serializers.compensation_event_serializers import (
            CompensationEventSerializer,
        )
        return Response(CompensationEventSerializer(events, many=True).data)


# ===========================================================================
# WRITER — Earnings
# ===========================================================================

class WriterEarningsView(APIView):
    """
    GET /writer/compensation/earnings/
        ?from_date=2026-05-01&to_date=2026-05-14

    Writer's own period earnings totals.
    """
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if not from_date or not to_date:
            return _error("from_date and to_date query params are required.", 400)

        result = EarningsQueryService.get_period_totals(
            website=website,
            start_date=from_date,
            end_date=to_date,
            writer=writer,
        )
        return Response(result)


class WriterRunningBalanceView(APIView):
    """
    GET /writer/compensation/balance/

    Returns pending balance (not yet matured) and
    running lifetime balance (all matured + paid).
    """
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        return Response({
            "pending": EarningsQueryService.get_pending_balance(
                website=website, writer=writer,
            ),
            "lifetime": EarningsQueryService.get_running_balance(
                website=website, writer=writer,
            ),
        })


class WriterBonusHistoryView(APIView):
    """
    GET /writer/compensation/bonuses/
        ?limit=20

    Writer's own bonus event history.
    """
    permission_classes = [IsWriter]

    def get(self, request):
        writer = _get_writer_profile(request)
        limit = int(request.query_params.get("limit", 20))
        events = BonusService.get_bonus_history(writer=writer, limit=limit)

        from writer_compensation.api.serializers.writer_payout_serializers import (
            WriterEventSerializer,
        )
        return Response(WriterEventSerializer(events, many=True).data)