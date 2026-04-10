from __future__ import annotations

from django.db.models import QuerySet

from ledger.models.journal_entry import JournalEntry
from ledger.models.journal_line import JournalLine


class JournalSelectors:
    """
    Read only queries for journal entries and lines.
    """

    @staticmethod
    def get_entries_for_website(*, website) -> QuerySet[JournalEntry]:
        return JournalEntry.objects.filter(
            website=website
        ).order_by("-created_at")

    @staticmethod
    def get_entry_by_id(
        *,
        website,
        entry_id,
    ) -> JournalEntry:
        return JournalEntry.objects.get(
            website=website,
            id=entry_id,
        )

    @staticmethod
    def get_entries_by_type(
        *,
        website,
        entry_type: str,
    ) -> QuerySet[JournalEntry]:
        return JournalEntry.objects.filter(
            website=website,
            entry_type=entry_type,
        ).order_by("-created_at")

    @staticmethod
    def get_entries_by_status(
        *,
        website,
        status: str,
    ) -> QuerySet[JournalEntry]:
        return JournalEntry.objects.filter(
            website=website,
            status=status,
        ).order_by("-created_at")

    @staticmethod
    def get_entries_by_reference(
        *,
        website,
        reference: str,
    ) -> QuerySet[JournalEntry]:
        return JournalEntry.objects.filter(
            website=website,
            reference=reference,
        ).order_by("-created_at")

    @staticmethod
    def get_entries_for_source_object(
        *,
        website,
        source_model: str,
        source_object_id: str,
    ) -> QuerySet[JournalEntry]:
        return JournalEntry.objects.filter(
            website=website,
            source_model=source_model,
            source_object_id=source_object_id,
        ).order_by("-created_at")

    @staticmethod
    def get_entry_lines(
        *,
        journal_entry: JournalEntry,
    ) -> QuerySet[JournalLine]:
        return JournalLine.objects.select_related(
            "ledger_account",
            "journal_entry",
        ).filter(
            journal_entry=journal_entry
        ).order_by("created_at", "id")

    @staticmethod
    def get_lines_for_wallet_reference(
        *,
        website,
        wallet_reference: str,
    ) -> QuerySet[JournalLine]:
        return JournalLine.objects.select_related(
            "ledger_account",
            "journal_entry",
        ).filter(
            website=website,
            wallet_reference=wallet_reference,
        ).order_by("-created_at")

    @staticmethod
    def get_lines_for_payment_intent(
        *,
        website,
        payment_intent_reference: str,
    ) -> QuerySet[JournalLine]:
        return JournalLine.objects.select_related(
            "ledger_account",
            "journal_entry",
        ).filter(
            website=website,
            payment_intent_reference=payment_intent_reference,
        ).order_by("-created_at")