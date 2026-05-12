from __future__ import annotations
 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
 
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
    PaymentWindowChangeRequestCreateSerializer,
)
from writer_compensation.api.serializers.payout_batch_serializers import (
    PayoutBatchSerializer,
    PayoutRecordSerializer,
)
from writer_compensation.api.serializers.writer_payout_serializers import (
    WriterCurrentWindowSerializer,
    WriterEventSerializer,
    WriterPayoutRecordSerializer,
    WriterPayoutPreferenceSerializer,
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
from writer_compensation.services.event_intake_service import (
    EventIntakeService,
)
from writer_compensation.services.cycle_change_service import (
    PaymentCycleChangeService,
)
 
 
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







class SupportWriterEventsView(APIView):
    """
    GET /support/writers/{writer_id}/events/
    Full event timeline for a writer — read only.
    """
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
    """
    GET /support/writers/{writer_id}/payouts/
    All payout items for a writer — read only.
    """
    permission_classes = [IsAdminOrSupport]
 
    def get(self, request, writer_id):
        try:
            from writer_management.models import WriterProfile
            writer = WriterProfile.objects.get(pk=writer_id)
        except Exception:
            return _error("Writer not found.", 404)
 
        items = PayoutSelectors.get_writer_payout_history(writer)
        return Response(PayoutRecordSerializer(items, many=True).data)
 
 
class SupportHeldRecordsView(APIView):
    """
    GET /support/held-items/
    All held payout items site-wide — support priority queue.
    """
    permission_classes = [IsAdminOrSupport]
 
    def get(self, request):
        website = _get_website(request)
        items   = AdminSelectors.get_held_items_site_wide(website)
        return Response(PayoutRecordSerializer(items, many=True).data)