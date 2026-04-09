from rest_framework import serializers

from ledger.models import LedgerAccount


class LedgerAccountSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = LedgerAccount
        fields = [
            "id",
            "website",
            "code",
            "name",
            "account_type",
            "currency",
            "status",
            "is_system_account",
            "allows_negative",
            "description",
            "metadata",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "created_at",
            "updated_at",
        ]