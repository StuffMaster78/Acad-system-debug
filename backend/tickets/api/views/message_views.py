from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response

from tickets.api.permissions import IsTicketParticipantOrStaff
from tickets.api.serializers import (
    TicketMessageCreateSerializer,
    TicketMessageSerializer,
)
from tickets.api.views.ticket_views import TicketPagination
from tickets.models import Ticket
from tickets.selectors import TicketMessageSelector, TicketSelector


class TicketMessageViewSet(viewsets.GenericViewSet):
    permission_classes = [IsTicketParticipantOrStaff]
    pagination_class = TicketPagination

    def get_serializer_class(self):
        if self.action == "create":
            return TicketMessageCreateSerializer
        return TicketMessageSerializer

    def list(self, request):
        ticket_id = request.query_params.get("ticket")
        if not ticket_id:
            return Response([])

        ticket = self._get_ticket(ticket_id=ticket_id)
        messages = TicketMessageSelector.for_ticket_visible_to_user(
            ticket=ticket,
            user=request.user,
        )
        page = self.paginate_queryset(messages)
        serializer = TicketMessageSerializer(page or messages, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def create(self, request):
        ticket = self._get_ticket(ticket_id=request.data.get("ticket"))
        serializer = self.get_serializer(
            data=request.data,
            context={**self.get_serializer_context(), "ticket": ticket},
        )
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(
            TicketMessageSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )

    def _get_ticket(self, *, ticket_id) -> Ticket:
        if not ticket_id:
            raise ValidationError({"ticket": "This field is required."})

        visible_ticket = TicketSelector.detail_visible_to_user(
            user=self.request.user,
        ).filter(id=ticket_id).first()
        if visible_ticket is not None:
            return visible_ticket

        if Ticket.objects.filter(id=ticket_id).exists():
            raise PermissionDenied("You do not have access to this ticket.")

        raise NotFound("Ticket not found.")
