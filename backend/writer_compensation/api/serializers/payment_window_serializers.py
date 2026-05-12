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
from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer,
)


class PaymentWindowSerializer(serializers.ModelSerializer):
    is_locked   = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()
 
    class Meta:
        model  = PaymentWindow
        fields = [
            "id",
            "cycle_type",
            "start_date",
            "end_date",
            "status",
            "is_locked",
            "is_editable",
            "closed_at",
            "processing_at",
            "done_at",
            "created_at",
        ]
        read_only_fields = fields
 
    def get_is_locked(self, obj) -> bool:
        return obj.is_locked
 
    def get_is_editable(self, obj) -> bool:
        return obj.is_editable
 
 
class PaymentWindowCreateSerializer(serializers.Serializer):
    cycle_type = serializers.ChoiceField(choices=CycleType.choices)
    start_date = serializers.DateField()
    end_date   = serializers.DateField()
 
    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError(
                "start_date must be before end_date."
            )
        return data
 
 
# ---------------------------------------------------------------------------
# WriterWindowDetail  (admin per-writer detail view)
# ---------------------------------------------------------------------------
 
class WriterWindowDetailSerializer(serializers.Serializer):
    """
    Powers the admin per-writer event detail panel.
    Combines events + totals + breakdown in one response.
    """
    events     = CompensationEventSerializer(many=True)
    gross      = serializers.DecimalField(max_digits=12, decimal_places=2)
    deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    net        = serializers.DecimalField(max_digits=12, decimal_places=2)
    count      = serializers.IntegerField()
    breakdown  = serializers.ListField(child=serializers.DictField())

class PaymentWindowChangeRequestSerializer(serializers.ModelSerializer):
    writer_name = serializers.SerializerMethodField()
 
    class Meta:
        model  = PaymentWindowChangeRequest
        fields = [
            "id",
            "writer_name",
            "from_cycle",
            "requested_cycle",
            "reason",
            "status",
            "rejection_reason",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = fields
 
    def get_writer_name(self, obj) -> str:
        u = obj.writer.user
        return u.get_full_name() or u.email
 
 
class PaymentWindowChangeRequestCreateSerializer(serializers.Serializer):
    requested_cycle = serializers.ChoiceField(choices=CycleType.choices)
    reason          = serializers.CharField(
        max_length=1000,
        required=False,
        default="",
    ) 
 
# ---------------------------------------------------------------------------
# PayoutItem
# ---------------------------------------------------------------------------
 
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


class PaymentWindowChangeRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(max_length=1000, required=False, default="")