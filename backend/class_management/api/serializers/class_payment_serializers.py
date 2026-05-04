from __future__ import annotations

from rest_framework import serializers

from class_management.models import (
    ClassInstallment,
    ClassInstallmentPlan,
    ClassInvoiceLink,
    ClassPaymentAllocation,
)


class ClassInstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInstallmentPlan
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ClassInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInstallment
        fields = "__all__"
        read_only_fields = [
            "paid_amount",
            "status",
            "paid_at",
            "payment_intent_id",
            "created_at",
            "updated_at",
        ]


class CreateEqualInstallmentPlanSerializer(serializers.Serializer):
    installment_count = serializers.IntegerField(min_value=1)
    due_dates = serializers.ListField(
        child=serializers.DateTimeField(),
        allow_empty=False,
    )
    deposit_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    allow_work_before_full_payment = serializers.BooleanField(default=True)
    pause_work_when_overdue = serializers.BooleanField(default=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class PrepareClassPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    use_wallet = serializers.BooleanField(default=False)
    installment_id = serializers.IntegerField(required=False, allow_null=True)


class ClassPaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPaymentAllocation
        fields = "__all__"


class ClassInvoiceLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInvoiceLink
        fields = "__all__"