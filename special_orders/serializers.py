from rest_framework import serializers
from .models import (
    SpecialOrder,
    InstallmentPayment,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    WriterBonus
)

class PredefinedSpecialOrderConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for predefined-cost special orders.
    """
    class Meta:
        model = PredefinedSpecialOrderConfig
        fields = '__all__'


class PredefinedSpecialOrderDurationSerializer(serializers.ModelSerializer):
    """
    Serializer for predefined special order durations.
    """
    class Meta:
        model = PredefinedSpecialOrderDuration
        fields = '__all__'


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for installment payments.
    """
    special_order_id = serializers.PrimaryKeyRelatedField(queryset=SpecialOrder.objects.all(), source='special_order', write_only=True)
    
    class Meta:
        model = InstallmentPayment
        fields = ['id', 'special_order_id', 'website', 'due_date', 'amount_due', 'is_paid']


class SpecialOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for special orders.
    """
    client_username = serializers.ReadOnlyField(source='client.username')
    writer_username = serializers.ReadOnlyField(source='writer.username')
    predefined_type = PredefinedSpecialOrderConfigSerializer(read_only=True)
    predefined_type_id = serializers.PrimaryKeyRelatedField(queryset=PredefinedSpecialOrderConfig.objects.all(), source='predefined_type', write_only=True)
    installments = InstallmentPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = SpecialOrder
        fields = [
            'id', 'client', 'client_username', 'writer', 'writer_username', 'order_type', 'predefined_type', 'predefined_type_id',
            'inquiry_details', 'admin_notes', 'total_cost', 'deposit_required', 'is_approved', 'status', 'duration_days', 
            'website', 'created_at', 'updated_at', 'installments'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WriterBonusSerializer(serializers.ModelSerializer):
    """
    Serializer for writer bonuses.
    """
    writer_username = serializers.ReadOnlyField(source='writer.username')
    special_order_id = serializers.PrimaryKeyRelatedField(queryset=SpecialOrder.objects.all(), source='special_order', write_only=True)

    class Meta:
        model = WriterBonus
        fields = ['id', 'writer', 'writer_username', 'special_order_id', 'website', 'amount', 'category', 'is_paid', 'granted_at']
        read_only_fields = ['granted_at']