"""
Serializers for streamlined class payment system.
"""
from rest_framework import serializers
from class_management.class_payment import (
    ClassPayment,
    ClassPaymentInstallment,
    ClassWriterPayment,
)
from class_management.models import ClassBundle, ClassInstallment


class ClassPaymentInstallmentSerializer(serializers.ModelSerializer):
    """Serializer for class payment installments."""
    installment_number = serializers.IntegerField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    paid_at = serializers.DateTimeField(read_only=True)
    payment_record_id = serializers.IntegerField(source='payment_record.id', read_only=True)
    due_date = serializers.DateField(source='class_installment.due_date', read_only=True)
    
    class Meta:
        model = ClassPaymentInstallment
        fields = [
            'id', 'installment_number', 'amount', 'is_paid', 'paid_at',
            'payment_record_id', 'due_date'
        ]


class ClassWriterPaymentSerializer(serializers.ModelSerializer):
    """Serializer for writer payments related to classes."""
    writer_username = serializers.CharField(source='class_payment.assigned_writer.username', read_only=True)
    bundle_id = serializers.IntegerField(source='class_payment.class_bundle.id', read_only=True)
    
    class Meta:
        model = ClassWriterPayment
        fields = [
            'id', 'amount', 'payment_type', 'installment_number',
            'is_paid', 'paid_at', 'writer_username', 'bundle_id', 'created_at'
        ]
        read_only_fields = ['created_at']


class ClassPaymentDetailSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for class payment details."""
    bundle_id = serializers.IntegerField(source='class_bundle.id', read_only=True)
    bundle_status = serializers.CharField(source='class_bundle.status', read_only=True)
    number_of_classes = serializers.IntegerField(source='class_bundle.number_of_classes', read_only=True)
    assigned_writer_username = serializers.CharField(
        source='assigned_writer.username',
        read_only=True,
        allow_null=True
    )
    installments = ClassPaymentInstallmentSerializer(many=True, read_only=True)
    writer_payments = ClassWriterPaymentSerializer(many=True, read_only=True)
    payment_progress = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ClassPayment
        fields = [
            'id', 'bundle_id', 'bundle_status', 'number_of_classes',
            'assigned_writer_username',
            'total_amount', 'deposit_amount', 'deposit_paid', 'balance_remaining',
            'client_payment_status', 'payment_progress',
            'writer_compensation_amount', 'writer_paid_amount', 'writer_payment_status',
            'uses_installments', 'total_installments', 'paid_installments',
            'installments', 'writer_payments',
            'created_at', 'updated_at', 'writer_paid_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'writer_paid_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        # Hide client payment info from writers
        if request and hasattr(request, 'user'):
            user = request.user
            if getattr(user, 'role', None) == 'writer':
                # Remove client payment fields for writers
                self.fields.pop('total_amount', None)
                self.fields.pop('deposit_amount', None)
                self.fields.pop('deposit_paid', None)
                self.fields.pop('balance_remaining', None)
                self.fields.pop('client_payment_status', None)
                self.fields.pop('payment_progress', None)
                self.fields.pop('uses_installments', None)
                self.fields.pop('total_installments', None)
                self.fields.pop('paid_installments', None)
                self.fields.pop('installments', None)


class ClassPaymentSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment summaries."""
    bundle_id = serializers.IntegerField(source='class_bundle.id', read_only=True)
    assigned_writer_username = serializers.CharField(
        source='assigned_writer.username',
        read_only=True,
        allow_null=True
    )
    payment_progress = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ClassPayment
        fields = [
            'id', 'bundle_id', 'assigned_writer_username',
            'total_amount', 'balance_remaining', 'client_payment_status',
            'writer_compensation_amount', 'writer_payment_status',
            'payment_progress', 'paid_installments', 'total_installments'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        # Hide client payment info from writers
        if request and hasattr(request, 'user'):
            user = request.user
            if getattr(user, 'role', None) == 'writer':
                # Remove client payment fields for writers
                self.fields.pop('total_amount', None)
                self.fields.pop('balance_remaining', None)
                self.fields.pop('client_payment_status', None)
                self.fields.pop('payment_progress', None)
                self.fields.pop('paid_installments', None)
                self.fields.pop('total_installments', None)

