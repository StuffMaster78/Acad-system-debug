"""
writer_compensation/api/views/financial_event_views.py
"""
from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.permissions.base import IsFinanceStaff
from writer_compensation.permissions.permissions import IsAdminUser


def _get_website(request):
    return request.website


class FinancialEventListView(generics.ListAPIView):
    serializer_class   = CompensationEventSerializer
    permission_classes = [IsFinanceStaff]

    def get_queryset(self):
        website = _get_website(self.request)
        return (
            CompensationEvent.objects
            .filter(website=website)
            .select_related("writer", "payment_window", "settlement_period")
            .order_by("-created_at")
        )


class FinancialEventDetailView(generics.RetrieveAPIView):
    serializer_class   = CompensationEventSerializer
    permission_classes = [IsFinanceStaff]

    def get_queryset(self):
        website = _get_website(self.request)
        return (
            CompensationEvent.objects
            .filter(website=website)
            .select_related("writer", "payment_window", "settlement_period")
        )


# ---------------------------------------------------------------------------
# End of financial_event_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/settlement_views.py
"""
from writer_compensation.api.serializers.settlement_serializers import (
    SettlementPeriodSerializer,
)
from writer_compensation.models.settlement_period import SettlementPeriod


class SettlementListView(generics.ListAPIView):
    serializer_class   = SettlementPeriodSerializer
    permission_classes = [IsFinanceStaff]

    def get_queryset(self):
        website = _get_website(self.request)
        return (
            SettlementPeriod.objects
            .filter(website=website)
            .select_related("writer", "payment_window")
            .order_by("-created_at")
        )


class SettlementDetailView(generics.RetrieveAPIView):
    serializer_class   = SettlementPeriodSerializer
    permission_classes = [IsFinanceStaff]

    def get_queryset(self):
        website = _get_website(self.request)
        return (
            SettlementPeriod.objects
            .filter(website=website)
            .select_related("writer", "payment_window")
        )


# ---------------------------------------------------------------------------
# End of settlement_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/settlement_actions_views.py
"""
from writer_compensation.exceptions.exceptions import CompensationError
from writer_compensation.facade.payments_facade import CompensationFacade
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.selectors.window_selectors import WindowSelectors


def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


class RunSettlementView(APIView):
    """
    POST /settlements/run/
    Run the full settlement pipeline for one writer in one window.
    Body: { writer_id, window_id, auto_finalize (optional, default true) }
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        website     = _get_website(request)
        writer_id   = request.data.get("writer_id")
        window_id   = request.data.get("window_id")
        auto_fin    = request.data.get("auto_finalize", True)

        if not writer_id or not window_id:
            return _error("writer_id and window_id are required.", 400)

        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
            window = PaymentWindow.objects.get(pk=window_id, website=website)
        except Exception as e:
            return _error(str(e), 404)

        try:
            period = CompensationFacade.run_settlement(
                website=website,
                writer=writer,
                payment_window=window,
                auto_finalize=auto_fin,
            )
        except (ValueError, CompensationError) as e:
            return _error(str(e), 409)

        from writer_compensation.api.serializers.settlement_serializers import (
            SettlementPeriodSerializer,
        )
        return Response(
            SettlementPeriodSerializer(period).data,
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# End of settlement_actions_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/exposure_views.py
"""
from writer_compensation.api.serializers.exposure_serializers import (
    ExposureLedgerSerializer,
)
from writer_compensation.exceptions.exceptions import CompensationError
from writer_compensation.facade.payments_facade import CompensationFacade
from writer_compensation.models.exposure_ledger import ExposureLedger
from writer_compensation.permissions.payout_permissions import CanViewPayouts


class ExposureLedgerListView(generics.ListAPIView):
    serializer_class   = ExposureLedgerSerializer
    permission_classes = [CanViewPayouts]

    def get_queryset(self):
        website = _get_website(self.request)
        return (
            ExposureLedger.objects
            .filter(website=website)
            .select_related("writer")
            .order_by("-last_updated")
        )


class ExposureLedgerDetailView(generics.RetrieveAPIView):
    serializer_class   = ExposureLedgerSerializer
    permission_classes = [CanViewPayouts]

    def get_queryset(self):
        website = _get_website(self.request)
        return ExposureLedger.objects.filter(website=website)


class ExposureRecomputeView(APIView):
    """
    POST /exposure/{pk}/recompute/
    Full authoritative recompute from raw event log.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        website = _get_website(request)
        try:
            ledger = ExposureLedger.objects.get(pk=pk, website=website)
        except ExposureLedger.DoesNotExist:
            return _error("Exposure ledger not found.", 404)

        try:
            ledger = CompensationFacade.recompute_exposure(
                website=website,
                writer=ledger.writer,
            )
        except CompensationError as e:
            return _error(str(e), 409)

        return Response(ExposureLedgerSerializer(ledger).data)


# ---------------------------------------------------------------------------
# End of exposure_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/reconciliation_actions_views.py
"""
from writer_compensation.api.serializers.reconcilliation_serializers import (
    ReconciliationReportSerializer,
    RunReconciliationSerializer,
)
from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.permissions.payout_permissions import CanReconcilePayouts


class RunReconciliationView(APIView):
    """
    POST /reconciliation/run/
    Generate or refresh a reconciliation report for a payout batch.
    Body: { batch_id, ledger_total, payout_total, cleared_total }
    """
    permission_classes = [CanReconcilePayouts]

    def post(self, request):
        website    = _get_website(request)
        serializer = RunReconciliationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated  = serializer.validated_data

        try:
            batch = PayoutBatch.objects.get(
                pk=validated["batch_id"],
                website=website,
            )
        except PayoutBatch.DoesNotExist:
            return _error("Batch not found.", 404)

        report = CompensationFacade.run_reconciliation(
            website=website,
            batch=batch,
            ledger_total=validated["ledger_total"],
            payout_total=validated["payout_total"],
            cleared_total=validated["cleared_total"],
        )

        return Response(
            ReconciliationReportSerializer(report).data,
            status=status.HTTP_201_CREATED,
        )


class ReconciliationReportListView(generics.ListAPIView):
    """
    GET /reconciliation/
    All reconciliation reports for this site.
    """
    serializer_class   = ReconciliationReportSerializer
    permission_classes = [CanReconcilePayouts]

    def get_queryset(self):
        from writer_compensation.models.payout_reconciliation_report import (
            PayoutReconciliationReport,
        )
        website = _get_website(self.request)
        return (
            PayoutReconciliationReport.objects
            .filter(website=website)
            .select_related("payout_batch")
            .order_by("-created_at")
        )


# ---------------------------------------------------------------------------
# End of reconciliation_actions_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/wallet_views.py
"""
from wallets.models import Wallet
from wallets.serializers import WalletSerializer
from writer_compensation.permissions.permissions import IsAdminUser as _IsAdmin


class WalletListView(generics.ListAPIView):
    serializer_class   = WalletSerializer
    permission_classes = [_IsAdmin]

    def get_queryset(self):
        website = _get_website(self.request)
        return Wallet.objects.filter(website=website)


class WalletDetailView(generics.RetrieveAPIView):
    serializer_class   = WalletSerializer
    permission_classes = [_IsAdmin]

    def get_queryset(self):
        website = _get_website(self.request)
        return Wallet.objects.filter(website=website)


# ---------------------------------------------------------------------------
# End of wallet_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/support_views.py
"""
from writer_compensation.permissions.permissions import IsAdminOrSupport
from writer_compensation.selectors.admin_selectors import AdminSelectors
from writer_compensation.selectors.payout_selectors import PayoutSelectors
from writer_compensation.selectors.writer_selectors import WriterSelectors
from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer,
)
from writer_compensation.api.serializers.payment_window_serializers import (
    PayoutRecordSerializer,
)


class SupportWriterEventsView(APIView):
    permission_classes = [IsAdminOrSupport]

    def get(self, request, writer_id):
        website = _get_website(request)
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        filters = {
            "event_type": request.query_params.get("event_type"),
            "status":     request.query_params.get("status"),
            "from_date":  request.query_params.get("from_date"),
            "to_date":    request.query_params.get("to_date"),
        }

        events  = WriterSelectors.get_writer_events(writer, website, filters)
        summary = WriterSelectors.get_writer_lifetime_summary(writer, website)

        return Response({
            "summary": summary,
            "events":  CompensationEventSerializer(events, many=True).data,
        })


class SupportWriterPayoutsView(APIView):
    permission_classes = [IsAdminOrSupport]

    def get(self, request, writer_id):
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)

        records = PayoutSelectors.get_writer_payout_history(writer)
        return Response(PayoutRecordSerializer(records, many=True).data)


class SupportHeldRecordsView(APIView):
    permission_classes = [IsAdminOrSupport]

    def get(self, request):
        website = _get_website(request)
        records = AdminSelectors.get_held_items_site_wide(website)
        return Response(PayoutRecordSerializer(records, many=True).data)


# ---------------------------------------------------------------------------
# End of support_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/writer_payout_views.py
"""
from writer_compensation.enums.compensation_enums import CycleType
from writer_compensation.exceptions.exceptions import CycleChangeNotAllowedError
from writer_compensation.permissions.permissions import IsWriter
from writer_compensation.selectors.payout_selectors import PayoutSelectors
from writer_compensation.selectors.writer_selectors import WriterSelectors
from writer_compensation.api.serializers.payment_window_serializers import (
    PaymentWindowChangeRequestCreateSerializer,
    PaymentWindowChangeRequestSerializer,
)
from writer_compensation.api.serializers.writer_payout_serializers import (
    WriterCurrentWindowSerializer,
    WriterEventSerializer,
    WriterPayoutPreferenceSerializer,
    WriterPayoutRecordSerializer,
)
from writer_compensation.services.cycle_change_service import PaymentCycleChangeService


def _get_writer_profile(request):
    return request.user.writer_profile


class WriterCurrentWindowView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer  = _get_writer_profile(request)
        data    = WriterSelectors.get_writer_current_window_status(writer, website)

        if data["window"] is None:
            return Response({
                "window":        None,
                "net":           "0.00",
                "count":         0,
                "is_processing": False,
            })

        return Response(WriterCurrentWindowSerializer(data).data)


class WriterEventListView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer  = _get_writer_profile(request)

        filters = {
            "event_type": request.query_params.get("event_type"),
            "status":     request.query_params.get("status"),
            "window_id":  request.query_params.get("window_id"),
            "from_date":  request.query_params.get("from_date"),
            "to_date":    request.query_params.get("to_date"),
        }

        events = WriterSelectors.get_writer_events(writer, website, filters)
        return Response(WriterEventSerializer(events, many=True).data)


class WriterPayoutHistoryView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        writer  = _get_writer_profile(request)
        records = PayoutSelectors.get_writer_payout_history(writer)
        return Response(WriterPayoutRecordSerializer(records, many=True).data)


class WriterLifetimeSummaryView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer  = _get_writer_profile(request)
        summary = WriterSelectors.get_writer_lifetime_summary(writer, website)
        return Response(summary)


class WriterPayoutPreferenceView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website    = _get_website(request)
        writer     = _get_writer_profile(request)
        preference = WriterSelectors.get_writer_payout_preference(writer, website)
        if not preference:
            return Response({"detail": "No preference set yet."}, 404)
        return Response(WriterPayoutPreferenceSerializer(preference).data)

    def post(self, request):
        from writer_compensation.models.writer_payout_preference import WriterPayoutPreference

        website = _get_website(request)
        writer  = _get_writer_profile(request)

        existing = WriterSelectors.get_writer_payout_preference(writer, website)
        if existing and existing.locked:
            return _error(
                "Your payout cycle is locked. Submit a cycle change request.",
                409,
            )

        cycle_type = request.data.get("cycle_type")
        if cycle_type not in dict(CycleType.choices):
            return _error("Invalid cycle_type.", 400)

        pref, _ = WriterPayoutPreference.objects.update_or_create(
            website=website,
            writer=writer,
            defaults={"cycle_type": cycle_type, "locked": True},
        )
        return Response(WriterPayoutPreferenceSerializer(pref).data)


class WriterCycleChangeRequestView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer  = _get_writer_profile(request)
        pending = WriterSelectors.get_pending_cycle_change_request(writer, website)
        if not pending:
            return Response({"detail": "No pending cycle change request."}, 404)
        return Response(PaymentWindowChangeRequestSerializer(pending).data)

    def post(self, request):
        website    = _get_website(request)
        writer     = _get_writer_profile(request)
        serializer = PaymentWindowChangeRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            change_request = PaymentCycleChangeService.request_change(
                website=website,
                writer=writer,
                requested_cycle=serializer.validated_data["requested_cycle"],
                reason=serializer.validated_data.get("reason", ""),
            )
        except CycleChangeNotAllowedError as e:
            return _error(str(e), 409)

        return Response(
            PaymentWindowChangeRequestSerializer(change_request).data,
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# End of writer_payout_views.py
# ---------------------------------------------------------------------------


"""
writer_compensation/api/views/advance_views.py
"""
from writer_compensation.api.serializers.advance_serializers import (
    AdvancePaymentRequestSerializer,
    ApproveAdvanceSerializer,
    RecordAdvanceRecoverySerializer,
    RequestAdvanceSerializer,
)
from writer_compensation.enums.compensation_enums import AdvancePaymentStatus
from writer_compensation.models.advance_payment import AdvancePaymentRequest
from writer_compensation.models.exposure_ledger import ExposureLedger
from writer_compensation.permissions.permissions import IsAdminUser, IsWriter
from writer_compensation.services.advance_payment_service import AdvancePaymentService


class WriterAdvanceRequestView(APIView):
    """
    GET  /advances/         — writer sees their own advance requests
    POST /advances/         — writer submits an advance request
    """
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer  = _get_writer_profile(request)
        qs      = (
            AdvancePaymentRequest.objects
            .filter(writer=writer, website=website)
            .prefetch_related("recoveries")
            .order_by("-created_at")
        )
        return Response(AdvancePaymentRequestSerializer(qs, many=True).data)

    def post(self, request):
        website    = _get_website(request)
        writer     = _get_writer_profile(request)
        serializer = RequestAdvanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ledger = ExposureLedger.objects.get(website=website, writer=writer)
        except ExposureLedger.DoesNotExist:
            return _error("No exposure ledger found. Contact support.", 404)

        if not AdvancePaymentService.can_request(
            ledger=ledger,
            amount=serializer.validated_data["amount"],
        ):
            from writer_compensation.services.risk_engine_service import RiskEngineService
            cap = RiskEngineService.get_advance_cap(ledger=ledger)
            return _error(
                f"Requested amount exceeds available advance capacity of ${cap}.",
                409,
            )

        advance = AdvancePaymentRequest.objects.create(
            website=website,
            writer=writer,
            payment_window=WriterSelectors.get_writer_current_window_status(
                writer, website,
            )["window"],
            requested_amount=serializer.validated_data["amount"],
            reason=serializer.validated_data["reason"],
            requested_by=request.user,
            status=AdvancePaymentStatus.PENDING,
        )
        return Response(
            AdvancePaymentRequestSerializer(advance).data,
            status=status.HTTP_201_CREATED,
        )


class AdminAdvanceListView(generics.ListAPIView):
    """GET /admin/advances/ — all advance requests for this site."""
    serializer_class   = AdvancePaymentRequestSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        website = _get_website(self.request)
        status_filter = self.request.query_params.get("status")
        qs = (
            AdvancePaymentRequest.objects
            .filter(website=website)
            .select_related("writer__account_profile__user", "payment_window")
            .prefetch_related("recoveries")
            .order_by("-created_at")
        )
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class AdminAdvanceApproveView(APIView):
    """POST /admin/advances/{pk}/approve/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        website = _get_website(request)
        try:
            advance = AdvancePaymentRequest.objects.get(pk=pk, website=website)
        except AdvancePaymentRequest.DoesNotExist:
            return _error("Advance request not found.", 404)

        if advance.status != AdvancePaymentStatus.PENDING:
            return _error(f"Cannot approve — status is {advance.status}.", 409)

        serializer = ApproveAdvanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            ledger = ExposureLedger.objects.get(
                website=website,
                writer=advance.writer,
            )
            AdvancePaymentService.apply_advance(
                website=website,
                writer=advance.writer,
                ledger=ledger,
                amount=validated["approved_amount"],
                created_by=request.user,
                advance_request=advance,
            )
        except (ValueError, Exception) as e:
            return _error(str(e), 409)

        advance.approved_amount = validated["approved_amount"]
        advance.admin_notes     = validated.get("admin_notes", "")
        advance.status          = AdvancePaymentStatus.APPROVED
        advance.reviewed_by     = request.user
        from django.utils import timezone
        advance.reviewed_at     = timezone.now()
        advance.save()

        return Response(AdvancePaymentRequestSerializer(advance).data)


class AdminAdvanceRejectView(APIView):
    """POST /admin/advances/{pk}/reject/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        website = _get_website(request)
        try:
            advance = AdvancePaymentRequest.objects.get(pk=pk, website=website)
        except AdvancePaymentRequest.DoesNotExist:
            return _error("Advance request not found.", 404)

        if advance.status != AdvancePaymentStatus.PENDING:
            return _error(f"Cannot reject — status is {advance.status}.", 409)

        from django.utils import timezone
        advance.status      = AdvancePaymentStatus.REJECTED
        advance.admin_notes = request.data.get("admin_notes", "")
        advance.reviewed_by = request.user
        advance.reviewed_at = timezone.now()
        advance.save()

        return Response(AdvancePaymentRequestSerializer(advance).data)


class AdminAdvanceRecoveryView(APIView):
    """POST /admin/advances/{pk}/recover/ — record a repayment instalment."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        website = _get_website(request)
        try:
            advance = AdvancePaymentRequest.objects.get(pk=pk, website=website)
        except AdvancePaymentRequest.DoesNotExist:
            return _error("Advance request not found.", 404)

        if advance.status not in {
            AdvancePaymentStatus.APPROVED,
            AdvancePaymentStatus.PARTIALLY_RECOVERED,
        }:
            return _error(
                f"Cannot record recovery — status is {advance.status}.", 409,
            )

        serializer = RecordAdvanceRecoverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            ledger = ExposureLedger.objects.get(website=website, writer=advance.writer)
            AdvancePaymentService.record_recovery(
                website=website,
                writer=advance.writer,
                ledger=ledger,
                advance_request=advance,
                amount=validated["amount"],
                notes=validated.get("notes", ""),
                created_by=request.user,
            )
        except (ValueError, Exception) as e:
            return _error(str(e), 409)

        advance.refresh_from_db()
        return Response(AdvancePaymentRequestSerializer(advance).data)


# ---------------------------------------------------------------------------
# End of advance_views.py
# ---------------------------------------------------------------------------