from __future__ import annotations

from rest_framework import serializers

from writer_compensation.models.exposure_ledger import (
    ExposureLedger,
)


class ExposureLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExposureLedger

        fields = [
            "id",
            "website",
            "writer",
            "total_earned",
            "total_bonuses",
            "total_deductions",
            "total_settled",
            "total_paid",
            "total_advance_taken",
            "recoverable_balance",
            "risk_cap_percentage",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields