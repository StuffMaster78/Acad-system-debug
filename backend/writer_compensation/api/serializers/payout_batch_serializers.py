from __future__ import annotations

from rest_framework import serializers

from writer_compensation.enums.compensation_enums import PayoutRecordStatus
from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.api.serializers.payment_window_serializers import (
    PaymentWindowSerializer,
    PayoutRecordSerializer,
)


class PayoutBatchSerializer(serializers.ModelSerializer):
    records = PayoutRecordSerializer(many=True, read_only=True) # FIX: was items
    payment_window = PaymentWindowSerializer(read_only=True) # FIX: was window
    paid_count = serializers.SerializerMethodField()
    held_count = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()

    class Meta:
        model = PayoutBatch
        fields = [
            "id",
            "payment_window", # FIX: was window
            "total_amount",
            "total_writers",
            "status",
            "paid_at",
            "paid_count",
            "held_count",
            "pending_count",
            "notes",
            "records", # FIX: was items
            "created_at",
        ]
        read_only_fields = fields

    def get_paid_count(self, obj) -> int:
        return obj.records.filter(
            status=PayoutRecordStatus.PAID, # FIX: was raw "paid"
        ).count()

    def get_held_count(self, obj) -> int:
        return obj.records.filter(
            status=PayoutRecordStatus.HELD, # FIX: was raw "held"
        ).count()

    def get_pending_count(self, obj) -> int:
        return obj.records.filter(
            status=PayoutRecordStatus.PENDING, # FIX: was raw "pending"
        ).count()