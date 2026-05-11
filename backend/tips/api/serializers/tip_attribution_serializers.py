from rest_framework import serializers
from tips.models.tip_attribution import TipAttribution


class TipAttributionSerializer(serializers.ModelSerializer):
    """
    Read-only attribution view.
    """

    tip_id = serializers.IntegerField(source="tip.id", read_only=True)

    class Meta:
        model = TipAttribution
        fields = [
            "id",
            "tip_id",
            "context_type",
            "context_id",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields