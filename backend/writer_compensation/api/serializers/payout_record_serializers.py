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
)


class PayoutRecordSerializer(serializers.ModelSerializer):
    writer_name       = serializers.SerializerMethodField()
    writer_email      = serializers.SerializerMethodField()
    confirmed_by_name = serializers.SerializerMethodField()
    paid_by_name      = serializers.SerializerMethodField()
 
    class Meta:
        model  = PayoutRecord
        fields = [
            "id",
            "writer_name",
            "writer_email",
            "total_amount",
            "status",
            "hold_reason",
            "confirmed_at",
            "confirmed_by_name",
            "paid_at",
            "paid_by_name",
            "notes",
        ]
        read_only_fields = fields
 
    def get_writer_name(self, obj) -> str:
        u = obj.writer.user
        return u.get_full_name() or u.email
 
    def get_writer_email(self, obj) -> str:
        return obj.writer.user.email
 
    def get_confirmed_by_name(self, obj) -> str | None:
        if obj.confirmed_by:
            return obj.confirmed_by.get_full_name() or obj.confirmed_by.email
        return None
 
    def get_paid_by_name(self, obj) -> str | None:
        if obj.paid_by:
            return obj.paid_by.get_full_name() or obj.paid_by.email
        return None
 
 
class PayoutRecordHoldSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=1000)
 
 
class PayoutRecordMarkPaidSerializer(serializers.Serializer):
    notes = serializers.CharField(max_length=1000, required=False, default="")
 
 
# ---------------------------------------------------------------------------
# PayoutBatch
# ---------------------------------------------------------------------------
 
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
        return obj.items.filter(status="paid").count()
 
    def get_held_count(self, obj) -> int:
        return obj.items.filter(status="held").count()
 
    def get_pending_count(self, obj) -> int:
        return obj.items.filter(status="pending").count()