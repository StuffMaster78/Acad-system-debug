from rest_framework import serializers
from .models import Wallet, WalletTransaction, WithdrawalRequest


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wallet model.
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = ['user', 'balance', 'last_updated']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for WalletTransaction model.
    """
    wallet = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = WalletTransaction
        fields = ['wallet', 'transaction_type', 'amount', 'description', 'created_at']


class WalletTopUpSerializer(serializers.Serializer):
    """
    Serializer for handling wallet top-ups (client-specific).
    """
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)


class WalletWithdrawSerializer(serializers.Serializer):
    """
    Serializer for handling wallet withdrawals (writer-specific).
    """
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for handling withdrawal requests.
    """
    class Meta:
        model = WithdrawalRequest
        fields = ['wallet', 'amount', 'status', 'description', 'created_at', 'processed_at']