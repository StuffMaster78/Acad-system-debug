from decimal import Decimal

from rest_framework import serializers

from payments_processor.enums import PaymentIntentPurpose, PaymentProvider

# Only wallet top-ups may go through the generic checkout endpoint.
# All other purposes (order, invoice, billing_payment_request, etc.) have
# dedicated service endpoints that resolve amounts server-side from the DB.
# Allowing arbitrary purposes here would let a client submit a tampered
# amount for an order payment.
_ALLOWED_CHECKOUT_PURPOSES = [
    (PaymentIntentPurpose.WALLET_TOP_UP, "Wallet Top Up"),
]


class PaymentCheckoutSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=PaymentProvider.choices)
    purpose = serializers.ChoiceField(choices=_ALLOWED_CHECKOUT_PURPOSES)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("1.00"))
    currency = serializers.CharField(required=False, default="USD")
    metadata = serializers.JSONField(required=False, default=dict)