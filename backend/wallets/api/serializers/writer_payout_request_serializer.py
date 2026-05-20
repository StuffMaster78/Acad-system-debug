from rest_framework import serializers

from wallets.models import WalletHold


class WriterPayoutRequestSerializer(serializers.ModelSerializer):
    wallet_id = serializers.IntegerField(source="wallet.id", read_only=True)
    writer_id = serializers.IntegerField(source="wallet.owner_user.id", read_only=True)
    writer_email = serializers.EmailField(source="wallet.owner_user.email", read_only=True)
    website_id = serializers.IntegerField(source="website.id", read_only=True)
    workflow_status = serializers.SerializerMethodField()

    class Meta:
        model = WalletHold
        fields = [
            "id",
            "website_id",
            "wallet_id",
            "writer_id",
            "writer_email",
            "amount",
            "status",
            "workflow_status",
            "reason",
            "reference",
            "reference_type",
            "metadata",
            "created_at",
            "updated_at",
            "released_at",
            "captured_at",
        ]
        read_only_fields = fields

    def get_workflow_status(self, obj):
        return (obj.metadata or {}).get("workflow_status")


class WriterPayoutRequestCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=10, required=False, default="USD")
    metadata = serializers.JSONField(required=False)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class WriterPayoutRequestActionSerializer(serializers.Serializer):
    review_notes = serializers.CharField(required=False, allow_blank=True, default="")
    external_reference = serializers.CharField(required=False, allow_blank=True, default="")
