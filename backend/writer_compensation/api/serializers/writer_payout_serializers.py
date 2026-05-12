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
    PaymentWindowSerializer
)
from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer
)

# ---------------------------------------------------------------------------
# Writer-facing serializers (minimal — no internal admin fields)
# ---------------------------------------------------------------------------

class WriterPayoutPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WriterPayoutPreference
        fields = ["id", "cycle_type", "locked", "created_at", "updated_at"]
        read_only_fields = fields
        
 
class WriterEventSerializer(serializers.ModelSerializer):
    """
    Writer sees their own events — no admin notes, no idempotency key,
    no hold reasons.
    """
    is_positive  = serializers.SerializerMethodField()
    window_label = serializers.SerializerMethodField()
    source_label = serializers.SerializerMethodField()
 
    class Meta:
        model  = CompensationEvent
        fields = [
            "id",
            "event_type",
            "amount",
            "status",
            "source_label",
            "is_positive",
            "window_label",
            "created_at",
        ]
        read_only_fields = fields
 
    def get_is_positive(self, obj) -> bool:
        return obj.amount > Decimal("0.00")
 
    def get_window_label(self, obj) -> str:
        w = obj.window
        return f"{w.start_date} – {w.end_date}"
 
    def get_source_label(self, obj) -> str | None:
        if obj.source_type and obj.source_id:
            return f"{obj.source_type.replace('_', ' ').title()} #{obj.source_id}"
        return None
 
 
class WriterPayoutRecordSerializer(serializers.ModelSerializer):
    """Writer sees their own payout items — no hold reason detail."""
    window_label = serializers.SerializerMethodField()
 
    class Meta:
        model  = PayoutRecord
        fields = [
            "id",
            "total_amount",
            "status",
            "window_label",
            "paid_at",
        ]
        read_only_fields = fields
 
    def get_window_label(self, obj) -> str:
        w = obj.batch.window
        return f"{w.start_date} – {w.end_date}"
 
 
class WriterCurrentWindowSerializer(serializers.Serializer):
    """What the writer dashboard shows for the current window."""
    window       = PaymentWindowSerializer()
    net          = serializers.DecimalField(max_digits=12, decimal_places=2)
    count        = serializers.IntegerField()
    is_processing = serializers.BooleanField()



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
 