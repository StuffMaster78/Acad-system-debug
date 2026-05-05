from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    SpecialOrderChangeRequest,
    SpecialOrderChangeRequestQuote,
)


class CreateChangeRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    pricing_impact = serializers.CharField(required=False)
    metadata = serializers.DictField(required=False)


class ReviewChangeRequestSerializer(serializers.Serializer):
    approve = serializers.BooleanField()
    decision_reason = serializers.CharField(required=False, allow_blank=True)
    estimated_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class CreateChangeQuoteSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False)


class ChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderChangeRequest
        fields = [
            "id",
            "special_order",
            "status",
            "pricing_impact",
            "title",
            "description",
            "requested_by",
            "reviewed_by",
            "reviewed_at",
            "decision_reason",
            "estimated_amount",
            "approved_amount",
            "metadata",
            "created_at",
            "updated_at",
        ]


class ChangeRequestQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderChangeRequestQuote
        fields = [
            "id",
            "change_request",
            "amount",
            "currency",
            "expires_at",
            "accepted_at",
            "rejected_at",
            "created_by",
            "metadata",
            "created_at",
            "updated_at",
        ]