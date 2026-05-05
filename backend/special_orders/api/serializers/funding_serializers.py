from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    SpecialOrderFundingMilestone,
    SpecialOrderFundingPlan,
    SpecialOrderPaymentApplication,
    SpecialOrderRefundApplication,
)


class SpecialOrderFundingMilestoneSerializer(serializers.ModelSerializer):
    balance_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    net_funded_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = SpecialOrderFundingMilestone
        fields = [
            "id",
            "milestone_type",
            "status",
            "sequence",
            "label",
            "amount_due",
            "funded_amount",
            "refunded_amount",
            "balance_amount",
            "net_funded_amount",
            "due_at",
            "required_before_staffing",
            "required_before_draft",
            "required_before_delivery",
            "required_before_completion",
            "created_at",
            "updated_at",
        ]


class SpecialOrderFundingPlanSerializer(serializers.ModelSerializer):
    milestones = SpecialOrderFundingMilestoneSerializer(
        many=True,
        read_only=True,
    )
    balance_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    net_funded_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = SpecialOrderFundingPlan
        fields = [
            "id",
            "special_order",
            "currency",
            "total_amount",
            "deposit_amount",
            "funded_amount",
            "refunded_amount",
            "balance_amount",
            "net_funded_amount",
            "status",
            "requires_full_payment_before_staffing",
            "requires_full_payment_before_delivery",
            "locked_at",
            "locked_by",
            "milestones",
            "created_at",
            "updated_at",
        ]


class SpecialOrderPaymentApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderPaymentApplication
        fields = [
            "id",
            "special_order",
            "funding_plan",
            "milestone",
            "source",
            "status",
            "amount",
            "currency",
            "idempotency_key",
            "payment_intent_reference",
            "payment_transaction_reference",
            "wallet_transaction_reference",
            "ledger_entry_reference",
            "applied_at",
            "applied_by",
            "metadata",
            "created_at",
            "updated_at",
        ]


class SpecialOrderRefundApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderRefundApplication
        fields = [
            "id",
            "special_order",
            "funding_plan",
            "milestone",
            "original_payment_application",
            "status",
            "destination",
            "amount",
            "currency",
            "refund_transaction_reference",
            "reversal_ledger_entry_reference",
            "reason",
            "requested_by",
            "approved_by",
            "refunded_at",
            "metadata",
            "created_at",
            "updated_at",
        ]