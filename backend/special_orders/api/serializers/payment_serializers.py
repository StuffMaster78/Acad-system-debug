from __future__ import annotations

from rest_framework import serializers


class CreatePaymentIntentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    milestone_id = serializers.IntegerField(required=False, allow_null=True)
    provider = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
    )
    metadata = serializers.DictField(required=False)


class ApplyExternalPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    idempotency_key = serializers.CharField(max_length=255)
    payment_intent_reference = serializers.CharField(max_length=255)
    payment_transaction_reference = serializers.CharField(max_length=255)
    ledger_entry_reference = serializers.CharField(max_length=255)
    milestone_id = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False)


class ApplyWalletPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    milestone_id = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False)


class ApplySplitPaymentSerializer(serializers.Serializer):
    wallet_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    external_amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    wallet_idempotency_key = serializers.CharField(max_length=255)
    external_idempotency_key = serializers.CharField(max_length=255)

    wallet_transaction_reference = serializers.CharField(max_length=255)
    payment_intent_reference = serializers.CharField(max_length=255)
    payment_transaction_reference = serializers.CharField(max_length=255)

    wallet_ledger_entry_reference = serializers.CharField(max_length=255)
    external_ledger_entry_reference = serializers.CharField(max_length=255)

    milestone_id = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False)