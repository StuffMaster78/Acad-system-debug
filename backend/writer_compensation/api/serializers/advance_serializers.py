from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from writer_compensation.models.advance_payment import (
    AdvancePaymentRequest,
    AdvanceRecovery,
)
from writer_compensation.enums.compensation_enums import AdvancePaymentStatus


class RequestAdvanceSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=500)

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Advance amount must be positive.")
        return value


class ApproveAdvanceSerializer(serializers.Serializer):
    approved_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    admin_notes = serializers.CharField(max_length=1000, required=False, default="")

    def validate_approved_amount(self, value: Decimal) -> Decimal:
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Approved amount must be positive.")
        return value


class RecordAdvanceRecoverySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(max_length=1000, required=False, default="")

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Recovery amount must be positive.")
        return value


class AdvanceRecoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceRecovery
        fields = ["id", "amount", "settlement_period", "notes", "recovered_at"]
        read_only_fields = fields


class AdvancePaymentRequestSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.SerializerMethodField()
    recoveries = AdvanceRecoverySerializer(many=True, read_only=True)
    writer_name = serializers.SerializerMethodField()

    class Meta:
        model = AdvancePaymentRequest
        fields = [
            "id",
            "writer_name",
            "payment_window",
            "status",
            "requested_amount",
            "approved_amount",
            "recovered_amount",
            "outstanding_balance",
            "reason",
            "admin_notes",
            "reviewed_at",
            "created_at",
            "recoveries",
        ]
        read_only_fields = fields

    def get_outstanding_balance(self, obj) -> Decimal:
        return obj.outstanding_balance

    def get_writer_name(self, obj) -> str:
        u = obj.writer.user
        return u.get_full_name() or u.email