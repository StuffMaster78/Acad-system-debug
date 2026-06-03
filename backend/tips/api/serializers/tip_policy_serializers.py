from rest_framework import serializers
from tips.models.tip_policy import TipPolicy


class TipPolicySerializer(serializers.ModelSerializer):
    """Full read/write serializer for TipPolicy — used in admin views."""

    class Meta:
        model = TipPolicy
        fields = [
            "id",
            "name",
            "slug",
            "description",
            # Core split
            "writer_percentage",
            "platform_percentage",
            # Limits
            "minimum_tip_amount",
            "risk_review_threshold",
            "maximum_tip_frequency_per_day",
            # Toggles
            "allow_wallet_tips",
            "allow_external_tips",
            "require_manual_review",
            # Status
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]


class TipPolicyUpdateSerializer(serializers.ModelSerializer):
    """Admin-controlled policy create/update."""

    class Meta:
        model = TipPolicy
        fields = [
            "name",
            "description",
            "writer_percentage",
            "platform_percentage",
            "minimum_tip_amount",
            "risk_review_threshold",
            "maximum_tip_frequency_per_day",
            "allow_wallet_tips",
            "allow_external_tips",
            "require_manual_review",
        ]
