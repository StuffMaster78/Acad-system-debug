from rest_framework import serializers

from payments_processor.enums import PaymentIntentPurpose, PaymentProvider


class PaymentCheckoutSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=PaymentProvider.choices)
    purpose = serializers.ChoiceField(choices=PaymentIntentPurpose.choices)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(required=False, default="USD")
    metadata = serializers.JSONField(required=False, default=dict)