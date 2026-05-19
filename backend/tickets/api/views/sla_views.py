from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tickets.api.permissions import IsTicketParticipantOrStaff, IsTicketStaff
from tickets.api.serializers import (
    TicketSLACreateSerializer,
    TicketSLASerializer,
)
from tickets.api.views.ticket_views import TicketPagination
from tickets.selectors import TicketSLASelector
from tickets.services import TicketSLAService
from tickets.sla_timers import TicketSLA


class TicketSLAViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTicketParticipantOrStaff]
    pagination_class = TicketPagination

    def get_queryset(self):
        qs = TicketSLASelector.visible_to_user(user=self.request.user)
        ticket_id = self.request.query_params.get("ticket")
        if ticket_id:
            qs = qs.filter(ticket_id=ticket_id)
        breached = self.request.query_params.get("breached")
        if breached == "true":
            qs = qs.filter(resolution_breached=True)
        elif breached == "false":
            qs = qs.filter(resolution_breached=False)
        priority = self.request.query_params.get("priority")
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return TicketSLACreateSerializer
        return TicketSLASerializer

    def perform_create(self, serializer):
        ticket = serializer.validated_data["ticket"]
        serializer.instance = TicketSLAService.ensure_for_ticket(ticket=ticket)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsTicketStaff],
    )
    def mark_first_response(self, request, pk=None):
        sla = self.get_object()
        sla.mark_first_response()
        return Response(TicketSLASerializer(sla).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsTicketStaff],
    )
    def mark_resolved(self, request, pk=None):
        sla = self.get_object()
        sla.mark_resolved()
        return Response(TicketSLASerializer(sla).data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsTicketStaff],
    )
    def check_breaches(self, request):
        slas = self.get_queryset()
        updated_count = TicketSLAService.check_breaches(queryset=slas)
        return Response(
            {
                "checked": slas.count(),
                "updated": updated_count,
            },
            status=status.HTTP_200_OK,
        )
