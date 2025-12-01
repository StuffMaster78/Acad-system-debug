from rest_framework import serializers
from writer_management.models.advance_payment import WriterAdvancePaymentRequest, AdvanceDeduction
from writer_management.services.advance_payment_service import AdvancePaymentService

class AdvanceDeductionSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_number = serializers.CharField(source='order.id', read_only=True)
    
    class Meta:
        model = AdvanceDeduction
        fields = [
            'id', 'amount_deducted', 'deducted_at',
            'order_id', 'order_number'
        ]

class WriterAdvancePaymentRequestSerializer(serializers.ModelSerializer):
    writer_username = serializers.CharField(source='writer.user.username', read_only=True)
    writer_email = serializers.EmailField(source='writer.user.email', read_only=True)
    writer_full_name = serializers.SerializerMethodField()
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    disbursed_by_username = serializers.CharField(source='disbursed_by.username', read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_fully_repaid = serializers.BooleanField(read_only=True)
    deductions = AdvanceDeductionSerializer(many=True, read_only=True)
    
    def get_writer_full_name(self, obj):
        return obj.writer.user.get_full_name() or obj.writer.user.username
    
    class Meta:
        model = WriterAdvancePaymentRequest
        fields = [
            'id', 'website', 'writer', 'writer_username', 'writer_email', 'writer_full_name',
            'requested_amount', 'approved_amount', 'disbursed_amount',
            'expected_earnings', 'max_advance_percentage', 'max_advance_amount',
            'status', 'reason', 'requested_at',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at', 'review_notes',
            'disbursed_by', 'disbursed_by_username', 'disbursed_at',
            'repaid_amount', 'fully_repaid_at', 'outstanding_amount',
            'is_fully_repaid', 'deductions'
        ]
        read_only_fields = [
            'expected_earnings', 'max_advance_amount', 'requested_at',
            'reviewed_at', 'disbursed_at', 'fully_repaid_at'
        ]

class AdvanceRequestCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

class AdvanceEligibilitySerializer(serializers.Serializer):
    """Serializer for advance eligibility information"""
    expected_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    max_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    max_advance_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_advances = serializers.DecimalField(max_digits=12, decimal_places=2)
    available_advance = serializers.DecimalField(max_digits=12, decimal_places=2)

class AdvanceApproveSerializer(serializers.Serializer):
    """Serializer for approving advance with optional counteroffer"""
    approved_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        help_text="Approved amount (counteroffer). If not provided, uses requested amount."
    )
    review_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notes explaining the approval or counteroffer"
    )

class AdvanceRejectSerializer(serializers.Serializer):
    """Serializer for rejecting advance"""
    review_notes = serializers.CharField(
        required=True,
        help_text="Reason for rejection (required)"
    )

