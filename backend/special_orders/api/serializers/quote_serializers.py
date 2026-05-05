from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    SpecialOrderPricingSnapshot,
    SpecialOrderQuote,
    SpecialOrderQuoteLine,
)


class SpecialOrderQuoteLineInputSerializer(serializers.Serializer):
    line_type = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(default=1, min_value=1)
    unit_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )


class CreateSpecialOrderQuoteSerializer(serializers.Serializer):
    line_items = SpecialOrderQuoteLineInputSerializer(many=True)
    expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )


class RejectSpecialOrderQuoteSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class SpecialOrderQuoteLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderQuoteLine
        fields = [
            "id",
            "line_type",
            "description",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
        ]


class SpecialOrderQuoteSerializer(serializers.ModelSerializer):
    lines = SpecialOrderQuoteLineSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = SpecialOrderQuote
        fields = [
            "id",
            "special_order",
            "status",
            "currency",
            "total_amount",
            "discount_amount",
            "expires_at",
            "created_by",
            "lines",
            "created_at",
            "updated_at",
        ]


class SpecialOrderPricingSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderPricingSnapshot
        fields = [
            "id",
            "special_order",
            "currency",
            "total_amount",
            "deposit_amount",
            "raw_data",
            "created_at",
        ]