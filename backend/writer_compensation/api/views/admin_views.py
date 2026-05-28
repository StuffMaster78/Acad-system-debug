from __future__ import annotations
 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from typing import Any, cast

from writer_compensation.exceptions.exceptions import (
    CompensationError,
    InvalidPayoutItemTransitionError,
    InvalidWindowTransitionError,
    NoOpenWindowError,
    WindowOverlapError,
)

from writer_compensation.models.payment_window import (
    PaymentWindow,
)
from writer_compensation.models.cycle_change_request import (
    PaymentWindowChangeRequest,
)
from writer_compensation.models.payout_batch import (
    PayoutBatch,
)
from writer_compensation.models.payout_record import (
    PayoutRecord,
)

from writer_compensation.permissions.permissions import (
    IsAdminOrSupport,
    IsAdminUser,
    IsSupport,
    IsWriter,
)
from writer_compensation.selectors.admin_selectors import (
    AdminSelectors,
    PayoutSelectors,
)
from writer_compensation.selectors.window_selectors import (
    WindowSelectors,
)
from writer_compensation.selectors.writer_selectors import (
    WriterSelectors,
)   

from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer,
)
from writer_compensation.api.serializers.payment_window_serializers import (
    PaymentWindowCreateSerializer,
    PaymentWindowSerializer,
    PaymentWindowChangeRequestSerializer,
    PaymentWindowChangeRejectSerializer,
)
from writer_compensation.api.serializers.payout_batch_serializers import (
    PayoutBatchSerializer,
)
from writer_compensation.api.serializers.writer_payout_serializers import (
    WriterWindowDetailSerializer,
)
from writer_compensation.api.serializers.payout_record_serializers import (
    PayoutRecordHoldSerializer,
    PayoutRecordMarkPaidSerializer,
    PayoutRecordSerializer,
)
from writer_compensation.api.serializers.adjustment_serializers import (
    PostCloseAdjustmentSerializer,
)
from writer_compensation.services.adjustment_service import (
    AdjustmentService,
)
from writer_compensation.services.window_service import (
    WindowService,
)
from writer_compensation.services.cycle_change_service import (
    PaymentCycleChangeService,
)
from writer_compensation.services.payout_engine_service import (
    PayoutEngineService,
)
from writer_compensation.enums.compensation_enums import WindowType
 
# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
 
def _get_writer_profile(request):
    return request.user.writer_profile
 
 
def _get_website(request):
    """
    Resolve website from request.
    Adjust this to match your website resolution strategy —
    e.g. from subdomain, header, or query param.
    """
    return request.website  # set by middleware
 
 
def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


# ===========================================================================
# ADMIN VIEWS — Window lifecycle
# ===========================================================================
 
class AdminWindowListCreateView(APIView):
    """
    GET  /admin/windows/ — list all windows for this site
    POST /admin/windows/ — create a new window
    """
    permission_classes = [IsAdminUser]
 
    def get(self, request):
        website = _get_website(request)
        windows = WindowSelectors.get_all_windows(website)
        return Response(
            PaymentWindowSerializer(windows, many=True).data
        )
 
    def post(self, request):
        website = _get_website(request)
        serializer = PaymentWindowCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)
        try:
            window = WindowService.create_window(
                website=website,
                created_by=request.user,
                **validated_data,
            )
        except WindowOverlapError as e:
            return _error(str(e), 409)
 
        return Response(
            PaymentWindowSerializer(window).data,
            status=status.HTTP_201_CREATED,
        )
 
 
class AdminWindowDetailView(APIView):
    """
    GET /admin/windows/{window_id}/
    Returns window info + batch summary + health counts.
    """
    permission_classes = [IsAdminOrSupport]
 
    def get(self, request, window_id):
        website = _get_website(request)
        window  = WindowSelectors.get_window_by_id(window_id, website)
        if not window:
            return _error("Window not found.", 404)
 
        batch  = PayoutSelectors.get_batch_for_window(window)
        health = AdminSelectors.get_window_health(window)
 
        return Response({
            "window": PaymentWindowSerializer(window).data,
            "batch":  PayoutBatchSerializer(batch).data if batch else None,
            "health": health,
        })
 
 
class AdminWindowCloseView(APIView):
    """
    POST /admin/windows/{window_id}/close/
    OPEN → CLOSED. Aggregates events. Creates batch + items.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, window_id):
        website = _get_website(request)
        window  = WindowSelectors.get_window_by_id(window_id, website)
        if not window:
            return _error("Window not found.", 404)
 
        # Warn if pending events exist — auto_confirm defaults to False.
        auto_confirm = request.data.get("auto_confirm_pending", False)
        pending_count = WindowSelectors.pending_event_count(window)
 
        try:
            window = WindowService.close_window(
                window,
                closed_by=request.user,
                auto_confirm_pending=auto_confirm,
            )
        except InvalidWindowTransitionError as e:
            return _error(str(e), 409)
 
        # Optionally auto-create the next window.
        if request.data.get("create_next_window", False):
            preference = request.data.get("next_cycle_type", window.cycle_type)
            WindowService.get_or_create_next_window(
                website=website,
                cycle_type=preference,
                after_window=window,
                created_by=request.user,
            )
 
        return Response({
            "status":            window.status,
            "pending_excluded":  pending_count if not auto_confirm else 0,
            "message": (
                f"{pending_count} PENDING events were excluded from this batch."
                if not auto_confirm and pending_count
                else "Window closed successfully."
            ),
        })
 
 
class AdminWindowStartProcessingView(APIView):
    """
    POST /admin/windows/{window_id}/start-processing/
    CLOSED → PROCESSING.
    Writers now see 'Payment being processed' on their dashboard.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, window_id):
        website = _get_website(request)
        window  = WindowSelectors.get_window_by_id(window_id, website)
        if not window:
            return _error("Window not found.", 404)
 
        try:
            window = WindowService.start_processing(window)
        except InvalidWindowTransitionError as e:
            return _error(str(e), 409)
 
        return Response({"status": window.status})
 
 
class AdminWindowMarkDoneView(APIView):
    """
    POST /admin/windows/{window_id}/mark-done/
    PROCESSING → DONE. Held items remain open.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, window_id):
        website = _get_website(request)
        window  = WindowSelectors.get_window_by_id(window_id, website)
        if not window:
            return _error("Window not found.", 404)
 
        try:
            window = WindowService.mark_done(window)
        except InvalidWindowTransitionError as e:
            return _error(str(e), 409)
 
        return Response({"status": window.status})
 
 
class AdminWindowAdjustView(APIView):
    """
    POST /admin/windows/{window_id}/adjust/
    Post-close adjustment for a writer — creates an ADJUSTMENT event
    in the next open window referencing this closed window.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, window_id):
        website       = _get_website(request)
        closed_window = WindowSelectors.get_window_by_id(window_id, website)
        if not closed_window:
            return _error("Window not found.", 404)
 
        serializer = PostCloseAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        try:
            from writer_management.models import WriterProfile
            validated_data = cast(dict[str, Any], serializer.validated_data)
            writer = WriterProfile.objects.get(
                pk=validated_data["writer_id"],
            )
        except Exception:
            return _error("Writer not found.", 404)
 
        try:

            validated_data = cast(dict[str, Any], serializer.validated_data)
            event = AdjustmentService.create_post_close_adjustment(
                closed_window=closed_window,
                writer=writer,
                amount=validated_data["amount"],
                notes=validated_data["notes"],
                created_by=request.user,
            )
        except (ValueError, NoOpenWindowError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response(
            CompensationEventSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )
 
 
# ===========================================================================
# ADMIN VIEWS — Writer event detail within a window
# ===========================================================================
 
class AdminWriterWindowEventsView(APIView):
    """
    GET /admin/windows/{window_id}/writers/{writer_id}/events/
    Full event detail for one writer in one window.
    Powers the per-writer admin drill-down.
    """
    permission_classes = [IsAdminOrSupport]
 
    def get(self, request, window_id, writer_id):
        website = _get_website(request)
        window  = WindowSelectors.get_window_by_id(window_id, website)
        if not window:
            return _error("Window not found.", 404)
 
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)
 
        events, totals  = WindowSelectors.get_writer_events_for_window(writer, window)
        breakdown = list(WindowSelectors.get_writer_event_breakdown(writer, window))
 
        data = WriterWindowDetailSerializer({
            "events": events,
            "gross": totals["gross"],
            "deductions": totals["deductions"],
            "net": totals["net"],
            "count": totals["count"],
            "breakdown": breakdown,
        }).data
 
        return Response(data)
 
 
class AdminWindowSummaryView(APIView):
    """
    GET /admin/windows/{window_id}/summary/
    Per-writer aggregate summary for a window — powers the batch table.
    """
    permission_classes = [IsAdminOrSupport]
 
    def get(self, request, window_id):
        website = _get_website(request)
        window  = WindowSelectors.get_window_by_id(window_id, website)
        if not window:
            return _error("Window not found.", 404)
 
        summary = list(WindowSelectors.get_window_summary(window))
        return Response(summary)
 
 
# ===========================================================================
# ADMIN VIEWS — Payout batch and items
# ===========================================================================
 
class AdminBatchDetailView(APIView):
    """
    GET /admin/batches/{batch_id}/
    Full batch with all payout items.
    """
    permission_classes = [IsAdminOrSupport]
 
    def get(self, request, batch_id):
        try:
            batch = (
                PayoutBatch.objects
                .prefetch_related("records__writer")
                .select_related("payment_window")
                .get(pk=batch_id)
            )
        except PayoutBatch.DoesNotExist:
            return _error("Batch not found.", 404)
 
        return Response(PayoutBatchSerializer(batch).data)
 
 
class AdminBatchBulkConfirmView(APIView):
    """
    POST /admin/batches/{batch_id}/bulk-confirm/
    Confirm all PENDING payout items in one action.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, batch_id):
        try:
            batch = PayoutBatch.objects.select_related("payment_window").get(pk=batch_id)
        except PayoutBatch.DoesNotExist:
            return _error("Batch not found.", 404)
 
        try:
            count = PayoutEngineService.bulk_confirm_all(batch, confirmed_by=request.user)
        except (InvalidWindowTransitionError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response({"confirmed": count})
 
 
class AdminBatchBulkMarkPaidView(APIView):
    """
    POST /admin/batches/{batch_id}/bulk-mark-paid/
    Mark all CONFIRMED items paid. Stamps underlying events as PAID.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, batch_id):
        try:
            batch = PayoutBatch.objects.select_related("payment_window").get(pk=batch_id)
        except PayoutBatch.DoesNotExist:
            return _error("Batch not found.", 404)
 
        try:
            count = PayoutEngineService.bulk_mark_paid(batch, paid_by=request.user)
        except (InvalidWindowTransitionError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response({"paid": count})
 
 
class AdminPayoutRecordConfirmView(APIView):
    """
    POST /admin/payout-items/{record_id}/confirm/
    Admin reviews one writer and confirms their total.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, record_id):
        try:
            record = PayoutRecord.objects.select_related(
                "batch__payment_window", "writer"
            ).get(pk=record_id)
        except PayoutRecord.DoesNotExist:
            return _error("Payout item not found.", 404)
 
        try:
            record = PayoutEngineService.confirm_record(record, confirmed_by=request.user)
        except (InvalidPayoutItemTransitionError, InvalidWindowTransitionError) as e:
            return _error(str(e), 409)
 
        return Response(PayoutRecordSerializer(record).data)
 
 
class AdminPayoutItemMarkPaidView(APIView):
    """
    POST /admin/payout-items/{record_id}/mark-paid/
    Admin has paid this writer externally — marks item PAID.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, record_id):
        try:
            record = PayoutRecord.objects.select_related(
                "batch__payment_window", "writer"
            ).get(pk=record_id)
        except PayoutRecord.DoesNotExist:
            return _error("Payout item not found.", 404)
 
        serializer = PayoutRecordMarkPaidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        try:
            validated_data = cast(dict[str, Any], serializer.validated_data)
            record = PayoutEngineService.mark_record_paid(
                record,
                paid_by=request.user,
                notes=validated_data["notes"],
                method=validated_data.get("method", ""),
                external_reference=validated_data.get("external_reference", ""),
            )
        except (InvalidPayoutItemTransitionError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response(PayoutRecordSerializer(record).data)
 
 
class AdminPayoutItemHoldView(APIView):
    """
    POST /admin/payout-items/{record_id}/hold/
    Hold one writer's payout — other writers in the batch unaffected.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, record_id):
        try:
            record = PayoutRecord.objects.select_related(
                "batch__payment_window", "writer"
            ).get(pk=record_id)
        except PayoutRecord.DoesNotExist:
            return _error("Payout item not found.", 404)
 
        serializer = PayoutRecordHoldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        try:
            validated_data = cast(dict[str, Any], serializer.validated_data)
            item = PayoutEngineService.hold_record(
                record,
                reason=validated_data["reason"],
                held_by=request.user,
            )
        except (InvalidPayoutItemTransitionError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response(PayoutRecordSerializer(item).data)
 
 
class AdminPayoutRecordReleaseView(APIView):
    """
    POST /admin/payout-items/{record_id}/release/
    Release a held item back to PENDING.
    """
    permission_classes = [IsAdminUser]
 
    def post(self, request, record_id):
        try:
            record = PayoutRecord.objects.select_related(
                "batch__payment_window", "writer"
            ).get(pk=record_id)
        except PayoutRecord.DoesNotExist:
            return _error("Payout item not found.", 404)
 
        try:
            record = PayoutEngineService.release_held_record(record, released_by=request.user)
        except (InvalidPayoutItemTransitionError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response(PayoutRecordSerializer(record).data)
 
 
# ===========================================================================
# ADMIN VIEWS — Cycle change requests
# ===========================================================================
 
class AdminCycleChangeListView(APIView):
    """
    GET /admin/cycle-changes/
    All pending cycle change requests for this site.
    """
    permission_classes = [IsAdminUser]
 
    def get(self, request):
        website  = _get_website(request)
        requests = AdminSelectors.get_all_cycle_change_requests(website)
        return Response(
            PaymentWindowChangeRequestSerializer(requests, many=True).data
        )
 
 
class AdminCycleChangeApproveView(APIView):
    """POST /admin/cycle-changes/{request_id}/approve/"""
    permission_classes = [IsAdminUser]
 
    def post(self, request, request_id):
        try:
            change_request = PaymentWindowChangeRequest.objects.get(pk=request_id)
        except PaymentWindowChangeRequest.DoesNotExist:
            return _error("Cycle change request not found.", 404)
 
        try:
            change_request = PaymentCycleChangeService.approve(
                change_request,
                reviewed_by=request.user,
            )
        except (ValueError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response(PaymentWindowChangeRequestSerializer(change_request).data)
 
 
class AdminCycleChangeRejectView(APIView):
    """POST /admin/cycle-changes/{request_id}/reject/"""
    permission_classes = [IsAdminUser]
 
    def post(self, request, request_id):
        try:
            change_request = PaymentWindowChangeRequest.objects.get(pk=request_id)
        except PaymentWindowChangeRequest.DoesNotExist:
            return _error("Cycle change request not found.", 404)
 
        serializer = PaymentWindowChangeRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        try:
            validated_data = cast(dict[str, Any], serializer.validated_data)
            change_request = PaymentCycleChangeService.reject(
                change_request,
                reviewed_by=request.user,
                rejection_reason=validated_data["rejection_reason"],
            )
        except (ValueError, CompensationError) as e:
            return _error(str(e), 409)
 
        return Response(PaymentWindowChangeRequestSerializer(change_request).data)