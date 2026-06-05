from rest_framework import serializers

from wallets.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    owner_user_id = serializers.IntegerField(source="owner_user.id", read_only=True)
    owner_user_email = serializers.EmailField(source="owner_user.email", read_only=True)
    owner_user_name = serializers.CharField(source="owner_user.full_name", read_only=True)
    owner_user_role = serializers.CharField(source="owner_user.role", read_only=True)
    website_id = serializers.IntegerField(source="website.id", read_only=True)
    website_name = serializers.CharField(source="website.name", read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            "id",
            "website_id",
            "website_name",
            "owner_user_id",
            "owner_user_email",
            "owner_user_name",
            "owner_user_role",
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

    def validate(self, attrs):
        if not (attrs.get("description") or "").strip():
            raise serializers.ValidationError(
                {"description": "Debit description is required."}
            )
        if not (attrs.get("reference") or "").strip():
            raise serializers.ValidationError(
                {"reference": "Debit reference is required."}
            )
        return attrs


class AdminEnsureWalletSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    user_lookup = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    wallet_type = serializers.ChoiceField(choices=["client", "writer"])
    currency = serializers.CharField(max_length=10, default="USD", required=False)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        user_lookup = (attrs.get("user_lookup") or "").strip()
        if not user_id and not user_lookup:
            raise serializers.ValidationError(
                "Provide either user_id or user_lookup."
            )
        attrs["user_lookup"] = user_lookup
        return attrs
