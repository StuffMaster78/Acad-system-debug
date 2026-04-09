from rest_framework import serializers

from ledger.models import JournalLine


class JournalLineSerializer(serializers.ModelSerializer):
    ledger_account_code = serializers.CharField(
        source="ledger_account.code",
        read_only=True,
    )
    ledger_account_name = serializers.CharField(
        source="ledger_account.name",
        read_only=True,
    )
    journal_entry_number = serializers.CharField(
        source="journal_entry.entry_number",
        read_only=True,
    )
    is_debit = serializers.ReadOnlyField()
    is_credit = serializers.ReadOnlyField()

    class Meta:
        model = JournalLine
        fields = [
            "id",
            "website",
            "journal_entry",
            "journal_entry_number",
            "ledger_account",
            "ledger_account_code",
            "ledger_account_name",
            "entry_side",
            "amount",
            "currency",
            "description",
            "user",
            "wallet_reference",
            "payment_intent_reference",
            "related_object_type",
            "related_object_id",
            "metadata",
            "is_debit",
            "is_credit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "journal_entry_number",
            "ledger_account_code",
            "ledger_account_name",
            "is_debit",
            "is_credit",
            "created_at",
            "updated_at",
        ]