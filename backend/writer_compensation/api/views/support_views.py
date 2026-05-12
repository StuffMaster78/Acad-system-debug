from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer,
)
from writer_compensation.api.serializers.payment_window_serializers import (
    PayoutRecordSerializer,
)
from writer_compensation.permissions.permissions import IsAdminOrSupport
from writer_compensation.selectors.admin_selectors import AdminSelectors
from writer_compensation.selectors.payout_selectors import PayoutSelectors
from writer_compensation.selectors.writer_selectors import WriterSelectors


def _get_website(request):
    return request.website


def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


class SupportWriterEventsView(APIView):
    """
    GET /support/writers/{writer_id}/events/
    Full event timeline for a writer — read only.
    Filterable: ?event_type=&status=&from_date=&to_date=
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
    Payout history for a writer — read only.
    """
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
    """
    GET /support/held-items/
    All held payout records site-wide — support priority queue.
    """
    permission_classes = [IsAdminOrSupport]

    def get(self, request):
        website = _get_website(request)
        records = AdminSelectors.get_held_items_site_wide(website)
        return Response(PayoutRecordSerializer(records, many=True).data)