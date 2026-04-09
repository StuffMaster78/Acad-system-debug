from rest_framework import serializers

from ledger.models import ReconciliationRecord


class ReconciliationSerializer(serializers.ModelSerializer):
    is_unreconciled = serializers.ReadOnlyField()
    is_matched = serializers.ReadOnlyField()
    is_partially_matched = serializers.ReadOnlyField()
    is_mismatched = serializers.ReadOnlyField()
    is_resolved = serializers.ReadOnlyField()
    is_final = serializers.ReadOnlyField()
    journal_entry_number = serializers.CharField(
        source="journal_entry.entry_number",
        read_only=True,
    )

    class Meta:
        model = ReconciliationRecord
        fields = [
            "id",
            "website",
            "journal_entry",
            "journal_entry_number",
            "user",
            "status",
            "currency",
            "expected_amount",
            "actual_amount",
            "matched_amount",
            "variance_amount",
            "reference",
            "external_reference",
            "payment_intent_reference",
            "source_app",
            "source_model",
            "source_object_id",
            "mismatch_reason",
            "resolved_by",
            "resolved_at",
            "reconciled_at",
            "metadata",
            "is_unreconciled",
            "is_matched",
            "is_partially_matched",
            "is_mismatched",
            "is_resolved",
            "is_final",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "journal_entry_number",
            "is_unreconciled",
            "is_matched",
            "is_partially_matched",
            "is_mismatched",
            "is_resolved",
            "is_final",
            "created_at",
            "updated_at",
        ]