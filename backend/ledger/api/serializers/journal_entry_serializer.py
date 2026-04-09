from typing import cast, Any
from rest_framework import serializers

from ledger.models import JournalEntry, JournalLine

from .journal_line_serializer import JournalLineSerializer


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = serializers.SerializerMethodField()
    is_draft = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    is_posted = serializers.ReadOnlyField()
    is_reversed = serializers.ReadOnlyField()
    is_failed = serializers.ReadOnlyField()
    is_final = serializers.ReadOnlyField()

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "website",
            "entry_number",
            "entry_type",
            "status",
            "currency",
            "description",
            "reference",
            "source_app",
            "source_model",
            "source_object_id",
            "external_reference",
            "payment_intent_reference",
            "triggered_by",
            "approved_by",
            "reversal_of",
            "effective_at",
            "posted_at",
            "metadata",
            "failure_reason",
            "is_draft",
            "is_pending",
            "is_posted",
            "is_reversed",
            "is_failed",
            "is_final",
            "lines",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "entry_number",
            "posted_at",
            "failure_reason",
            "is_draft",
            "is_pending",
            "is_posted",
            "is_reversed",
            "is_failed",
            "is_final",
            "lines",
            "created_at",
            "updated_at",
        ]

    def get_lines(self, obj: JournalEntry) -> list[dict[str, Any]]:
        entry_lines = JournalLine.objects.select_related(
            "ledger_account",
            "journal_entry",
        ).filter(
            journal_entry=obj
        ).order_by("created_at", "id")

        data = JournalLineSerializer(entry_lines, many=True).data
        return cast(list[dict[str, Any]], data)