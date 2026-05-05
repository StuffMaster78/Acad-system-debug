from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    EstimatedSpecialOrderSettings,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
)


class PredefinedSpecialOrderDurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredefinedSpecialOrderDuration
        fields = [
            "id",
            "duration_days",
            "price",
            "is_active",
        ]


class PredefinedSpecialOrderConfigSerializer(serializers.ModelSerializer):
    durations = PredefinedSpecialOrderDurationSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = PredefinedSpecialOrderConfig
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "requires_full_payment",
            "allow_wallet_payment",
            "allow_external_payment",
            "allow_discounts",
            "durations",
            "created_at",
            "updated_at",
        ]


class EstimatedSpecialOrderSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimatedSpecialOrderSettings
        fields = [
            "id",
            "default_deposit_percentage",
            "minimum_deposit_amount",
            "allow_installments",
            "require_deposit_before_staffing",
            "require_full_payment_before_delivery",
            "quote_expiry_hours",
            "allow_wallet_payment",
            "allow_external_payment",
            "allow_discounts",
            "created_at",
            "updated_at",
        ]