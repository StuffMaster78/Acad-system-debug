from __future__ import annotations

from rest_framework import serializers

from wallets.models import Wallet
from wallets.models import WalletEntry


class WalletSerializer(serializers.ModelSerializer):
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