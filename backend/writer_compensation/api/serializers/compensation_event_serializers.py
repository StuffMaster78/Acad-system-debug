"""
writer_compensation/api/serializers/compensation_event_serializers.py
"""
from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from writer_compensation.models.compensation_event import CompensationEvent


class CompensationEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    related_window_label = serializers.SerializerMethodField()
    is_positive = serializers.SerializerMethodField()
    window_label = serializers.SerializerMethodField()

    class Meta:
        model = CompensationEvent
        fields = [
            "id",
            "website",
            "writer",
            "event_type",
            "source",
            "status",
            "amount",
            "currency",
            "title",
            "description",
            "reference",
            "external_reference",
            "source_type",
            "source_id",
            "related_event",
            "settlement_period",
            "is_visible_to_writer",
            "is_risky",
            "is_locked",
            "matured_at",
            "disputed_at",
            "reversed_at",
            "is_positive",
            "window_label",
            "related_window_label",
            "created_by_name",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_locked",
            "settlement_period",
        ]

    def get_created_by_name(self, obj) -> str:
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return "System"

    def get_related_window_label(self, obj) -> str | None:
        if obj.related_window:
            w = obj.related_window
            return f"{w.start_date} – {w.end_date}"
        return None

    def get_is_positive(self, obj) -> bool:
        return obj.amount > Decimal("0.00")

    def get_window_label(self, obj) -> str:
        w = obj.payment_window # FIX: was obj.window
        return f"{w.start_date} – {w.end_date}"