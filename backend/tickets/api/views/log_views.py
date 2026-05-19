from __future__ import annotations

from rest_framework import filters, viewsets

from tickets.api.serializers import TicketLogSerializer
from tickets.api.views.ticket_views import TicketPagination
from tickets.models import TicketLog


class TicketLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketLogSerializer
    pagination_class = TicketPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        return TicketLog.objects.select_related(
            "ticket",
            "performed_by",
            "website",
        ).order_by("-timestamp")
