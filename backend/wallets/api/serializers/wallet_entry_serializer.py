from rest_framework import serializers

from wallets.models import WalletEntry


class WalletEntrySerializer(serializers.ModelSerializer):
    wallet_id = serializers.IntegerField(source="wallet.id", read_only=True)
    ledger_transaction_id = serializers.IntegerField(
        source="ledger_transaction.id",
        read_only=True,
    )
    website_id = serializers.IntegerField(source="website.id", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)

    class Meta:
        model = WalletEntry
        fields = [
            "id",
            "website_id",
            "wallet_id",
            "entry_type",
            "ledger_transaction_id",
            "direction",
            "status",
            "amount",
            "balance_before",
            "balance_after",
            "reference",
            "reference_type",
            "reference_id",
            "description",
            "metadata",
            "created_by_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields