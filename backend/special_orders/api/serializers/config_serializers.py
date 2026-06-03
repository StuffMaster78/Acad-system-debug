from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    EstimatedSpecialOrderSettings,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrderMilestoneTemplate,
    SpecialOrderMilestoneTemplateItem,
)
from special_orders.models.configs import (
    SpecialOrderRushSurchargeRule,
    SpecialOrderWriterLevelSurchargeRule,
    SpecialOrderClientTierDiscountRule,
    SpecialOrderPlatformDifficultyRule,
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
        read_only_fields = ["id"]


class PredefinedSpecialOrderConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)
    website_domain = serializers.CharField(source="website.domain", read_only=True)
    durations = PredefinedSpecialOrderDurationSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = PredefinedSpecialOrderConfig
        fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
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
        read_only_fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
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
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class SpecialOrderMilestoneTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderMilestoneTemplateItem
        fields = [
            "id",
            "sequence",
            "label",
            "percentage",
            "required_before_staffing",
            "required_before_delivery",
        ]


class SpecialOrderMilestoneTemplateSerializer(serializers.ModelSerializer):
    items = SpecialOrderMilestoneTemplateItemSerializer(many=True, read_only=True)

    class Meta:
        model = SpecialOrderMilestoneTemplate
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "items",
        ]


# ── Pricing rule serializers ──────────────────────────────────────────────────

class RushSurchargeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderRushSurchargeRule
        fields = ["id", "max_duration_days", "surcharge_percentage", "is_active"]
        read_only_fields = ["id"]


class WriterLevelSurchargeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderWriterLevelSurchargeRule
        fields = ["id", "writer_level", "surcharge_percentage", "is_active"]
        read_only_fields = ["id"]


class ClientTierDiscountRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderClientTierDiscountRule
        fields = ["id", "client_tier", "discount_percentage", "is_active"]
        read_only_fields = ["id"]


class DifficultyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderPlatformDifficultyRule
        fields = ["id", "platform", "difficulty_level", "multiplier", "is_active"]
        read_only_fields = ["id"]
