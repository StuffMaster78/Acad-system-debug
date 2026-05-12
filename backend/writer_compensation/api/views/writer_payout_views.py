from __future__ import annotations
 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.permissions.permissions import (
    IsWriter,
)
from writer_compensation.selectors.admin_selectors import (
    PayoutSelectors,
)
from writer_compensation.selectors.writer_selectors import (
    WriterSelectors,
)   

from writer_compensation.api.serializers.payment_window_serializers import (
    PaymentWindowChangeRequestSerializer,
    PaymentWindowChangeRequestCreateSerializer,
)
from writer_compensation.api.serializers.writer_payout_serializers import (
    WriterCurrentWindowSerializer,
    WriterEventSerializer,
    WriterPayoutRecordSerializer,
    WriterPayoutPreferenceSerializer,
)
from writer_compensation.services.cycle_change_service import (
    PaymentCycleChangeService,
)
from writer_compensation.enums.compensation_enums import CycleType
 

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




class WriterCurrentWindowView(APIView):
    """
    GET /writer/compensation/current-window/
    Current window status — shows PROCESSING banner if applicable.
    """
    permission_classes = [IsWriter]
 
    def get(self, request):
        website = _get_website(request)
        writer  = _get_writer_profile(request)
        data    = WriterSelectors.get_writer_current_window_status(writer, website)
 
        if data["window"] is None:
            return Response({
                "window": None,
                "net": "0.00",
                "count": 0,
                "is_processing": False,
            })
 
        return Response(
            WriterCurrentWindowSerializer(data).data
        )
 
 
class WriterEventListView(APIView):
    """
    GET /writer/compensation/events/
    Full event history for the authenticated writer.
    Filterable: ?event_type=tip&status=paid&from_date=2026-05-01
    """
    permission_classes = [IsWriter]
 
    def get(self, request):
        website = _get_website(request)
        writer  = _get_writer_profile(request)
 
        filters = {
            "event_type": request.query_params.get("event_type"),
            "status": request.query_params.get("status"),
            "window_id": request.query_params.get("window_id"),
            "from_date": request.query_params.get("from_date"),
            "to_date": request.query_params.get("to_date"),
        }
 
        events = WriterSelectors.get_writer_events(writer, website, filters)
        return Response(
            WriterEventSerializer(events, many=True).data
        )
 
 
class WriterPayoutHistoryView(APIView):
    """
    GET /writer/compensation/payouts/
    All payout items for the authenticated writer.
    """
    permission_classes = [IsWriter]
 
    def get(self, request):
        writer = _get_writer_profile(request)
        items = PayoutSelectors.get_writer_payout_history(writer)
        return Response(
            WriterPayoutRecordSerializer(items, many=True).data
        )
 
 
class WriterLifetimeSummaryView(APIView):
    """
    GET /writer/compensation/summary/
    Lifetime totals: earned, deductions, net, paid.
    """
    permission_classes = [IsWriter]
 
    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)
        summary = WriterSelectors.get_writer_lifetime_summary(writer, website)
        return Response(summary)
 
 
class WriterPayoutPreferenceView(APIView):
    """
    GET  /writer/compensation/preference/   — view current preference
    POST /writer/compensation/preference/   — set preference (first time only)
    """
    permission_classes = [IsWriter]
 
    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)
        preference = WriterSelectors.get_writer_payout_preference(writer, website)
        if not preference:
            return Response({"detail": "No preference set yet."}, status=404)
        return Response(WriterPayoutPreferenceSerializer(preference).data)
 
    def post(self, request):
        from writer_compensation.models.writer_payout_preference import WriterPayoutPreference
        from writer_compensation.exceptions.exceptions import CycleChangeNotAllowedError
 
        website = _get_website(request)
        writer = _get_writer_profile(request)
 
        existing = WriterSelectors.get_writer_payout_preference(writer, website)
        if existing and existing.locked:
            return _error(
                "Your payout cycle is locked. Submit a cycle change request to change it.",
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
    """
    POST /writer/compensation/cycle-change/
    Writer submits a cycle change request.
    """
    permission_classes = [IsWriter]
 
    def post(self, request):
        from writer_compensation.exceptions.exceptions import CycleChangeNotAllowedError
 
        website = _get_website(request)
        writer = _get_writer_profile(request)
        serializer = PaymentWindowChangeRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        try:
            change_request = PaymentCycleChangeService.request_change(
                website=website,
                writer=writer,
                requested_cycle=serializer.validated_data["requested_cycle"],
                reason=serializer.validated_data["reason"],
            )
        except CycleChangeNotAllowedError as e:
            return _error(str(e), 409)
 
        return Response(
            PaymentWindowChangeRequestSerializer(change_request).data,
            status=status.HTTP_201_CREATED,
        )