from rest_framework import serializers

from wallets.models import WalletHold


class WalletHoldSerializer(serializers.ModelSerializer):
    wallet_id = serializers.IntegerField(source="wallet.id", read_only=True)
    website_id = serializers.IntegerField(source="website.id", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)

    class Meta:
        model = WalletHold
        fields = [
            "id",
            "website_id",
            "wallet_id",
            "amount",
            "status",
            "reason",
            "reference",
            "reference_type",
            "reference_id",
            "expires_at",
            "released_at",
            "captured_at",
            "metadata",
            "created_by_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AdminCreateWalletHoldSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    reason = serializers.CharField(max_length=255)
    reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    reference_type = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
    )
    reference_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value