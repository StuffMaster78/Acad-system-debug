from rest_framework import serializers

from payments_processor.models import PaymentIntent


class PaymentIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIntent
        fields = [
            "id",
            "reference",
            "purpose",
            "provider",
            "status",
            "currency",
            "amount",
            "provider_intent_id",
            "expires_at",
            "paid_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields