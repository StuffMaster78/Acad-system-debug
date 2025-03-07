from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    WriterWallet, WalletTransaction, WriterPaymentBatch, PaymentSchedule, 
    ScheduledWriterPayment, PaymentOrderRecord, WriterPayment, AdminPaymentAdjustment, PaymentConfirmation
)
from .serializers import (
    WriterWalletSerializer, WalletTransactionSerializer, WriterPaymentBatchSerializer, PaymentScheduleSerializer,
    ScheduledWriterPaymentSerializer, PaymentOrderRecordSerializer, WriterPaymentSerializer, 
    AdminPaymentAdjustmentSerializer, PaymentConfirmationSerializer
)


class WriterWalletViewSet(viewsets.ModelViewSet):
    """ API endpoint for managing writer wallets. """
    queryset = WriterWallet.objects.all()
    serializer_class = WriterWalletSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """ Retrieve all transactions for a specific writer wallet. """
        wallet = self.get_object()
        transactions = WalletTransaction.objects.filter(writer_wallet=wallet)
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class WalletTransactionViewSet(viewsets.ModelViewSet):
    """ API endpoint for wallet transactions. """
    queryset = WalletTransaction.objects.all()
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterPaymentBatchViewSet(viewsets.ModelViewSet):
    """ API endpoint for managing payment batches. """
    queryset = WriterPaymentBatch.objects.all()
    serializer_class = WriterPaymentBatchSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["get"])
    def payments(self, request, pk=None):
        """ Retrieve all payments in a specific batch. """
        batch = self.get_object()
        payments = WriterPayment.objects.filter(batch=batch)
        serializer = WriterPaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    """ API endpoint for payment schedules. """
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleSerializer
    permission_classes = [permissions.IsAdminUser]


class ScheduledWriterPaymentViewSet(viewsets.ModelViewSet):
    """ API endpoint for scheduled writer payments. """
    queryset = ScheduledWriterPayment.objects.all()
    serializer_class = ScheduledWriterPaymentSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentOrderRecordViewSet(viewsets.ModelViewSet):
    """ API endpoint for order records related to writer payments. """
    queryset = PaymentOrderRecord.objects.all()
    serializer_class = PaymentOrderRecordSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterPaymentViewSet(viewsets.ModelViewSet):
    """ API endpoint for writer payments. """
    queryset = WriterPayment.objects.all()
    serializer_class = WriterPaymentSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminPaymentAdjustmentViewSet(viewsets.ModelViewSet):
    """ API endpoint for admin adjustments to writer payments. """
    queryset = AdminPaymentAdjustment.objects.all()
    serializer_class = AdminPaymentAdjustmentSerializer
    permission_classes = [permissions.IsAdminUser]


class PaymentConfirmationViewSet(viewsets.ModelViewSet):
    """ API endpoint for confirming payments. """
    queryset = PaymentConfirmation.objects.all()
    serializer_class = PaymentConfirmationSerializer
    permission_classes = [permissions.IsAdminUser]
