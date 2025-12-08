from rest_framework import serializers
from .models import (
    WriterWallet, WalletTransaction, WriterPaymentBatch, PaymentSchedule, 
    ScheduledWriterPayment, PaymentOrderRecord, WriterPayment, AdminPaymentAdjustment, PaymentConfirmation,
    WriterPaymentRequest
)

class WriterWalletSerializer(serializers.ModelSerializer):
    writer_username = serializers.CharField(source="writer.username", read_only=True)
    writer = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()

    class Meta:
        model = WriterWallet
        fields = "__all__"
    
    def get_writer(self, obj):
        """Get writer information"""
        if obj.writer:
            return {
                'id': obj.writer.id,
                'username': obj.writer.username,
                'email': obj.writer.email,
                'first_name': obj.writer.first_name,
                'last_name': obj.writer.last_name,
            }
        return None
    
    def get_website(self, obj):
        """Get website information"""
        if obj.website:
            return {
                'id': obj.website.id,
                'name': obj.website.name,
                'domain': obj.website.domain,
            }
        return None

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

class WriterPaymentRequestSerializer(serializers.ModelSerializer):
    writer_name = serializers.SerializerMethodField()
    writer_email = serializers.SerializerMethodField()
    reviewed_by_username = serializers.CharField(source="reviewed_by.username", read_only=True, allow_null=True)
    requested_by_username = serializers.CharField(source="requested_by.username", read_only=True)
    writer_wallet_data = serializers.SerializerMethodField()
    
    class Meta:
        model = WriterPaymentRequest
        fields = [
            'id', 'website', 'writer_wallet', 'requested_amount', 'available_balance',
            'status', 'reason', 'requested_by', 'reviewed_by', 'reviewed_at',
            'review_notes', 'created_at', 'processed_at', 'scheduled_payment',
            'writer_name', 'writer_email', 'reviewed_by_username', 'requested_by_username',
            'writer_wallet_data'
        ]
        read_only_fields = ['created_at', 'reviewed_at', 'processed_at']
    
    def get_writer_name(self, obj):
        try:
            if obj.writer_wallet and obj.writer_wallet.writer:
                user = obj.writer_wallet.writer
                # Try to get full name, fallback to username
                full_name = user.get_full_name()
                if full_name:
                    return full_name
                # Try to get registration_id from writer_profile
                try:
                    writer_profile = getattr(user, 'writer_profile', None)
                    if writer_profile and hasattr(writer_profile, 'registration_id'):
                        return writer_profile.registration_id
                except Exception:
                    pass
                return user.username or 'Unknown'
        except Exception:
            pass
        return 'Unknown'
    
    def get_writer_email(self, obj):
        try:
            if obj.writer_wallet and obj.writer_wallet.writer:
                return obj.writer_wallet.writer.email or ''
        except Exception:
            pass
        return ''
    
    def get_writer_wallet_data(self, obj):
        """Get writer wallet information for frontend"""
        try:
            if obj.writer_wallet and obj.writer_wallet.writer:
                writer = obj.writer_wallet.writer
                return {
                    'writer': {
                        'id': writer.id,
                        'username': writer.username or '',
                        'email': writer.email or '',
                        'first_name': writer.first_name or '',
                        'last_name': writer.last_name or '',
                    }
                }
        except Exception:
            pass
        return None