from rest_framework import serializers
from tips.models.tip_policy import TipPolicy


class TipPolicySerializer(serializers.ModelSerializer):
    """
    Read policy configuration.
    """

    class Meta:
        model = TipPolicy
        fields = [
            "id",
            "name",
            "writer_percentage",
            "platform_percentage",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields


class TipPolicyUpdateSerializer(serializers.ModelSerializer):
    """
    Admin-controlled policy updates.
    """

    class Meta:
        model = TipPolicy
        fields = [
            "writer_percentage",
            "platform_percentage",
            "is_active",
        ]