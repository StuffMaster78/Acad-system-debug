from __future__ import annotations

from rest_framework import serializers

from class_management.models import (
    ClassInstallment,
    ClassInstallmentPlan,
    ClassInvoiceLink,
    ClassPaymentAllocation,
)


class ClassPaymentScheduleSerializer(serializers.ModelSerializer):
    """Serialize a class payment schedule."""

    class Meta:
        model = ClassInstallmentPlan
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ClassPaymentMilestoneSerializer(serializers.ModelSerializer):
    """Serialize one scheduled class payment milestone."""

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


class CreateEqualPaymentScheduleSerializer(serializers.Serializer):
    """Validate equal-payment schedule creation."""

    milestone_count = serializers.IntegerField(min_value=1)
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

    def validate(self, attrs):
        """Keep the milestone count aligned with the submitted due dates."""
        milestone_count = attrs["milestone_count"]
        due_dates = attrs["due_dates"]

        if len(due_dates) != milestone_count:
            raise serializers.ValidationError(
                "Due dates must match milestone_count."
            )

        return attrs


class PrepareClassPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    use_wallet = serializers.BooleanField(default=False)
    payment_milestone_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    installment_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        """Accept the old installment_id while preferring milestone naming."""
        legacy_id = attrs.pop("installment_id", None)
        milestone_id = attrs.get("payment_milestone_id")

        if milestone_id and legacy_id and milestone_id != legacy_id:
            raise serializers.ValidationError(
                "Use either payment_milestone_id or installment_id."
            )

        if legacy_id and not milestone_id:
            attrs["payment_milestone_id"] = legacy_id

        return attrs


class ClassPaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPaymentAllocation
        fields = "__all__"


class ClassInvoiceLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInvoiceLink
        fields = "__all__"


# Backwards-compatible aliases while old callers migrate to payment schedules.
ClassInstallmentPlanSerializer = ClassPaymentScheduleSerializer
ClassInstallmentSerializer = ClassPaymentMilestoneSerializer
CreateEqualInstallmentPlanSerializer = CreateEqualPaymentScheduleSerializer
