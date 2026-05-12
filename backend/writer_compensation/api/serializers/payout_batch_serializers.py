from __future__ import annotations
 
from decimal import Decimal
 
from rest_framework import serializers
 
from writer_compensation.enums.compensation_enums import CycleType
from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)
from writer_compensation.models.cycle_change_request import (
    PaymentWindowChangeRequest,
)
from writer_compensation.models.payout_batch import (
    PayoutBatch,
)
from writer_compensation.models.payout_record import (
    PayoutRecord,
)
from writer_compensation.models.writer_payout_preference import (
    WriterPayoutPreference,
)
from writer_compensation.api.serializers.payment_window_serializers import (
    PaymentWindowSerializer,
    PayoutRecordSerializer,
)


class PayoutBatchSerializer(serializers.ModelSerializer):
    items         = PayoutRecordSerializer(many=True, read_only=True)
    window        = PaymentWindowSerializer(read_only=True)
    paid_count    = serializers.SerializerMethodField()
    held_count    = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()
 
    class Meta:
        model  = PayoutBatch
        fields = [
            "id",
            "window",
            "total_amount",
            "paid_at",
            "paid_count",
            "held_count",
            "pending_count",
            "notes",
            "items",
            "created_at",
        ]
        read_only_fields = fields
 
    def get_paid_count(self, obj) -> int:
        return obj.records.filter(status="paid").count()
 
    def get_held_count(self, obj) -> int:
        return obj.records.filter(status="held").count()
 
    def get_pending_count(self, obj) -> int:
        return obj.records.filter(status="pending").count()