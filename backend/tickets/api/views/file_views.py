from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from files_management.exceptions import FileManagementError
from files_management.enums import FilePurpose
from files_management.models import FileAttachment
from tickets.api.permissions import IsTicketParticipantOrStaff
from tickets.api.serializers import (
    TicketFileSerializer,
    TicketFileUploadSerializer,
)
from tickets.api.views.ticket_views import TicketPagination
from tickets.models import Ticket
from tickets.selectors import TicketSelector


class TicketFileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsTicketParticipantOrStaff]
    pagination_class = TicketPagination
    parser_classes = [MultiPartParser, FormParser]

    def list(self, request):
        ticket_id = request.query_params.get("ticket")
        if not ticket_id:
            return Response([])

        ticket = self._get_ticket(ticket_id=ticket_id)
        files = self._files_for_ticket(ticket=ticket)
        page = self.paginate_queryset(files)
        serializer = TicketFileSerializer(page or files, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def create(self, request):
        ticket = self._get_ticket(ticket_id=request.data.get("ticket"))
        serializer = TicketFileUploadSerializer(
            data=request.data,
            context={**self.get_serializer_context(), "ticket": ticket},
        )
        serializer.is_valid(raise_exception=True)
        try:
            attachment = serializer.save()
        except FileManagementError as exc:
            raise ValidationError({"file": str(exc)}) from exc
        return Response(
            TicketFileSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        attachment = get_object_or_404(
            FileAttachment.objects.select_related(
                "managed_file",
                "external_link",
                "attached_by",
                "content_type",
            ),
            pk=pk,
            purpose=FilePurpose.SUPPORT_ATTACHMENT,
            is_active=True,
        )
        self.check_object_permissions(request, attachment)
        return Response(TicketFileSerializer(attachment).data)

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

    def _files_for_ticket(self, *, ticket):
        content_type = ContentType.objects.get_for_model(
            ticket,
            for_concrete_model=False,
        )
        qs = FileAttachment.objects.filter(
            website=ticket.website,
            content_type=content_type,
            object_id=ticket.id,
            purpose=FilePurpose.SUPPORT_ATTACHMENT,
            is_active=True,
        ).select_related("managed_file", "external_link", "attached_by")

        if getattr(self.request.user, "role", None) not in {
            "admin",
            "superadmin",
            "support",
            "editor",
        }:
            qs = qs.exclude(visibility__in=["internal_only", "staff_only"])

        return qs.order_by("-attached_at")
