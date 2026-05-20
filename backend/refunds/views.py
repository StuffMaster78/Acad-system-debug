from __future__ import annotations

from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from refunds.models import Refund, RefundLog, RefundReceipt
from refunds.serializers import (
    RefundLogSerializer,
    RefundReceiptSerializer,
    RefundSerializer,
)
from refunds.services.refunds_processor import RefundProcessorService


class RefundPagination(PageNumberPagination):
    """Pagination for refund lists."""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class RefundViewSet(viewsets.ModelViewSet):
    """Refund request and processing endpoints."""

    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RefundPagination

    def get_queryset(self):
        user = self.request.user
        base_qs = Refund.objects.select_related(
            "website",
            "order",
            "order_payment",
            "payment_refund",
            "client",
            "processed_by",
        )
        if user.is_staff:
            return base_qs
        return base_qs.filter(client=user)

    def update(self, *args, **kwargs):
        return Response(
            {"detail": "Refunds cannot be updated."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, *args, **kwargs):
        return Response(
            {"detail": "Refunds cannot be deleted."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=["post"], url_path="retry")
    def retry_refund(self, request, pk=None):
        """
        Retry a rejected refund by returning it to pending.
        """
        refund = self.get_object()
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff can retry refunds."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if refund.status != Refund.REJECTED:
            return Response(
                {"error": "Only rejected refunds can be retried."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refund.status = Refund.PENDING
        refund.error_message = ""
        refund.save(update_fields=["status", "error_message", "updated_at"])
        return self._process(refund=refund, request=request)

    @action(detail=True, methods=["post"], url_path="process")
    def process_refund(self, request, pk=None):
        """Process a pending refund. Staff action only."""
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff can process refunds."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refund = self.get_object()
        if refund.status != Refund.PENDING:
            return Response(
                {"error": "Only pending refunds can be processed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self._process(refund=refund, request=request)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_refund(self, request, pk=None):
        """Cancel a pending refund request."""
        refund = self.get_object()
        if not request.user.is_staff and refund.client_id != request.user.pk:
            return Response(
                {"error": "You can only cancel your own refunds."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            RefundProcessorService.reject_refund(
                refund=refund,
                processed_by=request.user,
                reason=request.data.get("reason", "Refund manually canceled"),
            )
        except ValidationError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"success": "Refund canceled successfully."},
            status=status.HTTP_200_OK,
        )

    def _process(self, *, refund: Refund, request) -> Response:
        try:
            processed = RefundProcessorService.process_refund(
                refund=refund,
                processed_by=request.user,
                reason=request.data.get("reason", "Refund processed"),
                admin_user=request.user,
            )
        except ValidationError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return Response(
                {"error": f"Failed to process refund: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            self.get_serializer(processed).data,
            status=status.HTTP_200_OK,
        )


class RefundLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only refund audit endpoint."""

    serializer_class = RefundLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RefundPagination

    def get_queryset(self):
        user = self.request.user
        base_qs = RefundLog.objects.select_related(
            "website",
            "order",
            "refund",
            "client",
            "processed_by",
        )
        if user.is_staff:
            return base_qs
        return base_qs.filter(client=user)


class RefundReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only refund receipt endpoint."""

    serializer_class = RefundReceiptSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RefundPagination

    def get_queryset(self):
        user = self.request.user
        base_qs = RefundReceipt.objects.select_related(
            "website",
            "refund",
            "order_payment",
            "client",
            "processed_by",
        )
        if user.is_staff:
            return base_qs
        return base_qs.filter(client=user)
