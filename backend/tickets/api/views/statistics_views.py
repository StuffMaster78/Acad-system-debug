from __future__ import annotations

from django.db.models import Avg, Case, Count, DurationField, ExpressionWrapper, F, Q, When
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tickets.api.serializers import TicketStatisticsSerializer
from tickets.models import Ticket, TicketStatistics


class TicketStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketStatisticsSerializer
    queryset = TicketStatistics.objects.select_related("website").order_by(
        "-created_at",
    )

    @method_decorator(cache_page(60))
    @action(detail=False, methods=["get"], url_path="generate")
    def generate_statistics(self, request):
        resolution_duration = ExpressionWrapper(
            Case(
                When(status="closed", then=F("resolution_time") - F("created_at")),
                default=None,
                output_field=DurationField(),
            ),
            output_field=DurationField(),
        )
        stats = Ticket.objects.aggregate(
            total_tickets=Count("id"),
            resolved_tickets=Count("id", filter=Q(status="closed")),
            avg_resolution_time=Avg(resolution_duration),
        )
        duration = stats["avg_resolution_time"]
        stats["avg_resolution_time_seconds"] = (
            duration.total_seconds() if duration is not None else None
        )
        stats["avg_resolution_time"] = (
            str(duration) if duration is not None else None
        )
        return Response(stats, status=status.HTTP_200_OK)
