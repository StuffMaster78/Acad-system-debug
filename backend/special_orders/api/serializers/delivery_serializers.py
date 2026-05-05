from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    SpecialOrderCompletionLog,
    SpecialOrderDeliverable,
    SpecialOrderDeliveryCheckpoint,
)


class CreateDeliverableSerializer(serializers.Serializer):
    file_reference = serializers.CharField(max_length=255)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.DictField(required=False)


class SpecialOrderDeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderDeliverable
        fields = [
            "id",
            "special_order",
            "title",
            "description",
            "status",
            "file_reference",
            "uploaded_by",
            "reviewed_by",
            "uploaded_at",
            "reviewed_at",
            "delivered_at",
            "review_notes",
            "metadata",
            "created_at",
            "updated_at",
        ]


class DeliveryCheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderDeliveryCheckpoint
        fields = [
            "id",
            "special_order",
            "checkpoint_type",
            "status",
            "required_milestone",
            "unlocked_at",
            "unlocked_by",
            "waiver_reason",
            "metadata",
            "created_at",
            "updated_at",
        ]


class CompletionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderCompletionLog
        fields = [
            "id",
            "special_order",
            "completed_by",
            "action",
            "justification",
            "metadata",
            "created_at",
            "updated_at",
        ]