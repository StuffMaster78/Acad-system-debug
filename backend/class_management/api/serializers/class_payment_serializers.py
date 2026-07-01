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


class ManualVerifiedClassPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_reference = serializers.CharField(max_length=255)
    verification_note = serializers.CharField(max_length=1000)
    payment_method = serializers.CharField(
        max_length=80,
        required=False,
        allow_blank=True,
    )

    def validate_transaction_reference(self, value: str) -> str:
        value = value.strip()
        if len(value) < 4:
            raise serializers.ValidationError(
                "Transaction reference must be at least 4 characters."
            )
        return value

    def validate_verification_note(self, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError(
                "Verification note must be at least 10 characters."
            )
        return value


class ClassPaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPaymentAllocation
        fields = "__all__"


class ClassInvoiceLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInvoiceLink
        fields = "__all__"


class EditInstallmentSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=120, required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    due_at = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Provide at least one field to update.")
        return attrs


class MarkInstallmentPaidSerializer(serializers.Serializer):
    transaction_reference = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    note = serializers.CharField(
        max_length=1000, required=False, allow_blank=True, default=""
    )


# Backwards-compatible aliases while old callers migrate to payment schedules.
ClassInstallmentPlanSerializer = ClassPaymentScheduleSerializer
ClassInstallmentSerializer = ClassPaymentMilestoneSerializer
CreateEqualInstallmentPlanSerializer = CreateEqualPaymentScheduleSerializer
