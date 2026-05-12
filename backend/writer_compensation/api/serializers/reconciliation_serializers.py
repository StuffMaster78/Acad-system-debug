from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from writer_compensation.models.payout_reconciliation_report import (
    PayoutReconciliationReport,
)


class ReconciliationReportSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PayoutReconciliationReport

        fields = [
            "id",
            "website",
            "payout_batch",
            "total_ledger_amount",
            "total_payout_amount",
            "total_cleared_amount",
            "mismatch_amount",
            "status",
            "created_at",
        ]

        read_only_fields = fields


class RunReconciliationSerializer(serializers.Serializer):
    website_id = serializers.IntegerField()

    payout_batch_id = serializers.IntegerField()

    ledger_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payout_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    cleared_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )