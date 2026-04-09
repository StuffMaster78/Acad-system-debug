from rest_framework import serializers

from wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    owner_user_id = serializers.IntegerField(source="owner_user.id", read_only=True)
    website_id = serializers.IntegerField(source="website.id", read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "id",
            "website_id",
            "owner_user_id",
            "wallet_type",
            "currency",
            "status",
            "is_active",
            "available_balance",
            "pending_balance",
            "total_credited",
            "total_debited",
            "last_activity_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AdminWalletAdjustmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    description = serializers.CharField(max_length=500)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    reference_type = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="admin_adjustment",
    )
    reference_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )
    metadata = serializers.JSONField(required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class AdminWalletFundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default="Wallet funded by admin",
    )
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    reference_type = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="admin_funding",
    )
    reference_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )
    metadata = serializers.JSONField(required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class AdminWalletDebitSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default="Wallet debited by admin",
    )
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    reference_type = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="admin_debit",
    )
    reference_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )
    metadata = serializers.JSONField(required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value