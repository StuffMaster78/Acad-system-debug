from __future__ import annotations

from rest_framework import serializers

from writer_payments_management.models.financial_event_models import (
    FinancialEvent,
)


class FinancialEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialEvent

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