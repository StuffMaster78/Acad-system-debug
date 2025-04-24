from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Refund, RefundLog, RefundReceipt
from .serializers import (
    RefundSerializer,
    RefundLogSerializer,
    RefundReceiptSerializer,
)
from .services import process_refund


class RefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all().select_related('order_payment', 'client')
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Refund.objects.all()
        return Refund.objects.filter(client=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refund = serializer.save()
        process_refund(refund, request.user)
        return Response(
            self.get_serializer(refund).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, *args, **kwargs):
        return Response(
            {"detail": "Refunds cannot be updated."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, *args, **kwargs):
        return Response(
            {"detail": "Refunds cannot be deleted."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=True, methods=['post'], url_path='retry')
    def retry_refund(self, request, pk=None):
        refund = self.get_object()

        if not request.user.is_staff:
            return Response(
                {"error": "Only staff can retry refunds."},
                status=status.HTTP_403_FORBIDDEN
            )

        if refund.status != Refund.REJECTED:
            return Response(
                {"error": "Only rejected refunds can be retried."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            process_refund_logic(refund, request.user)
            return Response(
                {"success": "Refund retried and processed."},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_refund(self, request, pk=None):
        refund = self.get_object()

        if refund.status != Refund.PENDING:
            return Response(
                {"error": "Only pending refunds can be canceled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        refund.status = Refund.REJECTED
        refund.error_message = "Refund manually canceled"
        refund.processed_by = request.user
        refund.processed_at = timezone.now()
        refund.save()

        return Response(
            {"success": "Refund canceled successfully."},
            status=status.HTTP_200_OK
        )

class RefundLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RefundLog.objects.all().select_related('order')
    serializer_class = RefundLogSerializer
    permission_classes = [IsAuthenticated]


class RefundReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RefundReceipt.objects.all().select_related('refund')
    serializer_class = RefundReceiptSerializer
    permission_classes = [IsAuthenticated]