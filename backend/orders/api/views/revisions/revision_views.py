from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.api.permissions.revision_permissions import CanRequestRevision
from orders.api.serializers.revisions.revision_request_serializer import RevisionRequestSerializer
from orders.models import Order
from orders.models.revisions.order_revision_request import OrderRevisionRequest
from orders.models.orders.enums import OrderRevisionStatus
from orders.services.revision_orchestration_service import RevisionOrchestrationService


class RevisionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRevisionRequest
        fields = [
            "id",
            "status",
            "reason",
            "scope_summary",
            "writer_notes",
            "is_within_free_window",
            "approved_at",
            "submitted_at",
            "accepted_at",
            "rejected_at",
            "created_at",
            "updated_at",
        ]


class RevisionRequestView(GenericAPIView):
    """
    GET  orders/<id>/revisions/  — list all revision requests for an order
    POST orders/<id>/revisions/  — create a new revision request
    """

    serializer_class = RevisionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, order_id: int, *args: Any, **kwargs: Any) -> Response:
        order = self._get_order(request, order_id)
        qs = OrderRevisionRequest.objects.filter(
            website=order.website,
            order=order,
        ).order_by("-created_at")
        return Response(RevisionListSerializer(qs, many=True).data)

    def post(self, request: Request, order_id: int, *args: Any, **kwargs: Any) -> Response:
        self.permission_classes = [permissions.IsAuthenticated, CanRequestRevision]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        order = self._get_order(request, order_id)
        self.check_object_permissions(request, order)

        result = RevisionOrchestrationService.create_revision_request(
            order=order,
            requested_by=request.user,
            reason=validated_data["reason"],
            scope_summary=validated_data["scope_summary"],
            is_within_original_scope=validated_data["is_within_original_scope"],
            triggered_by=request.user,
        )

        if hasattr(result, "adjustment_type"):
            return Response(
                {
                    "routing": "paid_adjustment",
                    "message": "This revision is outside the free window and has been routed to a paid adjustment.",
                    "adjustment_request_id": result.pk,
                    "status": result.status,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            RevisionListSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_order(request: Request, order_id: int) -> Order:
        user = cast(Any, request.user)
        return get_object_or_404(
            Order.objects.select_related("website", "client", "preferred_writer"),
            pk=order_id,
            website=user.website,
        )


class RevisionApproveView(APIView):
    """POST orders/<id>/revisions/<rev_id>/approve/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, rev_id: int, *args: Any, **kwargs: Any) -> Response:
        rev = self._get_revision(request, order_id, rev_id)
        if rev.status != OrderRevisionStatus.PENDING:
            return Response({"detail": "Only pending revisions can be approved."}, status=status.HTTP_400_BAD_REQUEST)
        rev.status = OrderRevisionStatus.APPROVED
        rev.reviewed_by = request.user
        rev.approved_at = timezone.now()
        rev.save(update_fields=["status", "reviewed_by", "approved_at", "updated_at"])
        return Response(RevisionListSerializer(rev).data)


class RevisionRejectView(APIView):
    """POST orders/<id>/revisions/<rev_id>/reject/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, rev_id: int, *args: Any, **kwargs: Any) -> Response:
        rev = self._get_revision(request, order_id, rev_id)
        if rev.status not in {OrderRevisionStatus.PENDING, OrderRevisionStatus.APPROVED}:
            return Response({"detail": "Cannot reject a revision in this state."}, status=status.HTTP_400_BAD_REQUEST)
        rev.status = OrderRevisionStatus.REJECTED
        rev.reviewed_by = request.user
        rev.rejected_at = timezone.now()
        rev.save(update_fields=["status", "reviewed_by", "rejected_at", "updated_at"])
        return Response(RevisionListSerializer(rev).data)


class RevisionCompleteView(APIView):
    """POST orders/<id>/revisions/<rev_id>/complete/ — writer marks revision work done"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, rev_id: int, *args: Any, **kwargs: Any) -> Response:
        rev = self._get_revision(request, order_id, rev_id)
        if rev.status not in {OrderRevisionStatus.APPROVED, OrderRevisionStatus.IN_PROGRESS}:
            return Response({"detail": "Revision must be approved before it can be completed."}, status=status.HTTP_400_BAD_REQUEST)
        writer_notes = (request.data or {}).get("writer_notes", "")
        rev.status = OrderRevisionStatus.SUBMITTED
        rev.writer_notes = writer_notes
        rev.submitted_at = timezone.now()
        rev.save(update_fields=["status", "writer_notes", "submitted_at", "updated_at"])
        return Response(RevisionListSerializer(rev).data)


class RevisionAcceptView(APIView):
    """POST orders/<id>/revisions/<rev_id>/accept/ — client or admin accepts the completed revision"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, rev_id: int, *args: Any, **kwargs: Any) -> Response:
        rev = self._get_revision(request, order_id, rev_id)
        if rev.status != OrderRevisionStatus.SUBMITTED:
            return Response({"detail": "Only submitted revisions can be accepted."}, status=status.HTTP_400_BAD_REQUEST)
        rev.status = OrderRevisionStatus.ACCEPTED
        rev.accepted_at = timezone.now()
        rev.save(update_fields=["status", "accepted_at", "updated_at"])
        return Response(RevisionListSerializer(rev).data)


def _get_revision(request: Request, order_id: int, rev_id: int) -> OrderRevisionRequest:
    user = cast(Any, request.user)
    return get_object_or_404(
        OrderRevisionRequest.objects.select_related("order__website"),
        pk=rev_id,
        order_id=order_id,
        website=user.website,
    )


RevisionApproveView._get_revision = staticmethod(_get_revision)
RevisionRejectView._get_revision = staticmethod(_get_revision)
RevisionCompleteView._get_revision = staticmethod(_get_revision)
RevisionAcceptView._get_revision = staticmethod(_get_revision)
