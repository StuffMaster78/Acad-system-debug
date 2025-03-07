from rest_framework import serializers
from .models import (
    WriterWallet, WalletTransaction, WriterPaymentBatch, PaymentSchedule, 
    ScheduledWriterPayment, PaymentOrderRecord, WriterPayment, AdminPaymentAdjustment, PaymentConfirmation
)

class WriterWalletSerializer(serializers.ModelSerializer):
    writer_username = serializers.CharField(source="writer.username", read_only=True)

    class Meta:
        model = WriterWallet
        fields = "__all__"

class WalletTransactionSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source="writer_wallet.writer.username", read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = "__all__"

class WriterPaymentBatchSerializer(serializers.ModelSerializer):
    processed_by_username = serializers.CharField(source="processed_by.username", read_only=True)

    class Meta:
        model = WriterPaymentBatch
        fields = "__all__"

class PaymentScheduleSerializer(serializers.ModelSerializer):
    processed_by_username = serializers.CharField(source="processed_by.username", read_only=True)

    class Meta:
        model = PaymentSchedule
        fields = "__all__"

class ScheduledWriterPaymentSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source="writer_wallet.writer.username", read_only=True)

    class Meta:
        model = ScheduledWriterPayment
        fields = "__all__"

class PaymentOrderRecordSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source="payment.writer_wallet.writer.username", read_only=True)
    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = PaymentOrderRecord
        fields = "__all__"

class WriterPaymentSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source="writer_wallet.writer.username", read_only=True)
    
    class Meta:
        model = WriterPayment
        fields = "__all__"

class AdminPaymentAdjustmentSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source="writer_wallet.writer.username", read_only=True)
    adjusted_by_username = serializers.CharField(source="adjusted_by.username", read_only=True)

    class Meta:
        model = AdminPaymentAdjustment
        fields = "__all__"

class PaymentConfirmationSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source="writer_wallet.writer.username", read_only=True)

    class Meta:
        model = PaymentConfirmation
        fields = "__all__"