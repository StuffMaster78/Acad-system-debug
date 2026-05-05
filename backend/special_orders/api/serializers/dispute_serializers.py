from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    SpecialOrderDispute,
    SpecialOrderDisputeResolution,
)


class OpenDisputeSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False)


class ResolveDisputeSerializer(serializers.Serializer):
    resolution_type = serializers.CharField(max_length=50)
    notes = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    refund_application_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    metadata = serializers.DictField(required=False)


class RejectDisputeSerializer(serializers.Serializer):
    reason = serializers.CharField()


class DisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderDispute
        fields = [
            "id",
            "special_order",
            "status",
            "title",
            "description",
            "opened_by",
            "assigned_to",
            "opened_at",
            "resolved_at",
            "metadata",
            "created_at",
            "updated_at",
        ]


class DisputeResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderDisputeResolution
        fields = [
            "id",
            "dispute",
            "special_order",
            "resolution_type",
            "amount",
            "currency",
            "notes",
            "resolved_by",
            "refund_application",
            "metadata",
            "created_at",
            "updated_at",
        ]