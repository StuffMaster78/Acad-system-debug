from __future__ import annotations

from rest_framework import serializers

from wallets.models.wallet import Wallet
from wallets.models.wallet_entry import WalletEntry


class WalletSerializer(serializers.ModelSerializer):
    owner = serializers.IntegerField(source="owner_user_id", read_only=True)
    locked_balance = serializers.DecimalField(
        source="pending_balance", max_digits=14, decimal_places=2, read_only=True
    )
    total_inflow = serializers.DecimalField(
        source="total_credited", max_digits=14, decimal_places=2, read_only=True
    )
    total_outflow = serializers.DecimalField(
        source="total_debited", max_digits=14, decimal_places=2, read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Wallet

        fields = [
            "id",
            "website",
            "owner",
            "currency",
            "available_balance",
            "locked_balance",
            "total_inflow",
            "total_outflow",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


class WalletEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletEntry

        fields = [
            "id",
            "wallet",
            "entry_type",
            "amount",
            "balance_before",
            "balance_after",
            "reference",
            "description",
            "created_at",
        ]

        read_only_fields = fields