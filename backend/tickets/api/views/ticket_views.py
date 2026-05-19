from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from tickets.api.filters import TicketFilter
from tickets.api.permissions import IsTicketParticipantOrStaff, IsTicketStaff
from tickets.api.serializers import (
    TicketAssignSerializer,
    TicketCloseSerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    TicketReopenSerializer,
    TicketUpdateSerializer,
)
from tickets.selectors import TicketSelector
from tickets.services import TicketService


class TicketPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTicketParticipantOrStaff]
    pagination_class = TicketPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = TicketFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if self.action == "retrieve":
            return TicketSelector.detail_visible_to_user(user=self.request.user)
        return TicketSelector.visible_to_user(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return TicketCreateSerializer
        if self.action in {"update", "partial_update"}:
            return TicketUpdateSerializer
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        output = TicketDetailSerializer(ticket, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsTicketStaff],
    )
    def assign(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = TicketService.assign(
            ticket=ticket,
            assigned_to=serializer.validated_data["assigned_to"],
            actor=request.user,
        )
        return Response(TicketDetailSerializer(ticket).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsTicketStaff],
    )
    def escalate(self, request, pk=None):
        ticket = TicketService.escalate(
            ticket=self.get_object(),
            actor=request.user,
        )
        return Response(TicketDetailSerializer(ticket).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsTicketStaff],
    )
    def close(self, request, pk=None):
        serializer = TicketCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = TicketService.close(
            ticket=self.get_object(),
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(TicketDetailSerializer(ticket).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsTicketStaff],
    )
    def reopen(self, request, pk=None):
        serializer = TicketReopenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = TicketService.reopen(
            ticket=self.get_object(),
            actor=request.user,
            status=serializer.validated_data.get("status", "open"),
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(TicketDetailSerializer(ticket).data)
