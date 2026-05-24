from __future__ import annotations

from rest_framework import serializers

from writer_compensation.models.settlement_period import (
    SettlementPeriod,
)
from writer_compensation.models.settlement_item import (
    SettlementItem,
)


class SettlementItemSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="included_at", read_only=True)

    class Meta:
        model = SettlementItem

        fields = [
            "id",
            "financial_event",
            "amount",
            "created_at",
        ]

        read_only_fields = fields


class SettlementPeriodSerializer(serializers.ModelSerializer):
    items = SettlementItemSerializer(
        source="settlement_items",
        many=True,
        read_only=True,
    )

    class Meta:
        model = SettlementPeriod

        fields = [
            "id",
            "website",
            "writer",
            "payment_window",
            "status",
            "gross_earnings",
            "total_tips",
            "total_bonuses",
            "total_adjustments",
            "total_fines",
            "total_deductions",
            "total_advances",
            "total_reversals",
            "net_payable",
            "total_financial_events",
            "total_settlement_items",
            "is_locked",
            "locked_at",
            "finalized_at",
            "created_at",
            "updated_at",
            "items",
        ]

        read_only_fields = fields
