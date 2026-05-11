from rest_framework import serializers
from tips.models.tip import Tip

class CreateTipSerializer(serializers.Serializer):
    """
    Serializer for creating a tip.

    This only validates input. No business logic.
    """

    receiver_id = serializers.IntegerField()
    gross_amount_cents = serializers.IntegerField()
    
    currency = serializers.CharField(default="USD")

    context_type = serializers.CharField()
    context_id = serializers.UUIDField(required=False, allow_null=True)

    payment_intent_id = serializers.CharField(required=False, allow_blank=True)
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    idempotency_key = serializers.CharField()

class TipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tip
        fields = "__all__"

class TipSettleSerializer(serializers.Serializer):
    tip_id = serializers.IntegerField()


class TipMetricsQuerySerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)