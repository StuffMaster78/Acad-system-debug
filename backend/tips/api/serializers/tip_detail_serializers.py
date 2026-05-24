from rest_framework import serializers
from tips.models.tip import Tip


class TipDetailSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a Tip.
    """

    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    receiver_id = serializers.IntegerField(source="receiver.id", read_only=True)
    message = serializers.CharField(source="client_note", read_only=True)

    class Meta:
        model = Tip
        fields = [
            "id",
            "sender_id",
            "receiver_id",
            "gross_amount_cents",
            "writer_share_cents",
            "platform_fee_cents",
            "status",
            "message",
            "currency",
            "payment_intent_id",
            "created_at",
        ]
        read_only_fields = fields
