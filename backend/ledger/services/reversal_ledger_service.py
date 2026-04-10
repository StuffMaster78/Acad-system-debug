from __future__ import annotations

from typing import Any

from django.db import transaction

from ledger.constants import EntrySide, JournalEntryStatus, LedgerEntryType
from ledger.exceptions import LedgerReversalError
from ledger.models import JournalEntry, JournalLine
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)


class ReversalLedgerService:
    """
    Create compensating reversal entries for posted journal entries.
    """

    @staticmethod
    def _get_reversed_side(entry_side: str) -> str:
        """
        Return the opposite journal side.
        """
        if entry_side == EntrySide.DEBIT:
            return EntrySide.CREDIT

        return EntrySide.DEBIT

    @staticmethod
    @transaction.atomic
    def reverse_entry(
        *,
        journal_entry: JournalEntry,
        triggered_by=None,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Reverse a posted journal entry by creating a compensating entry.
        """
        if journal_entry.status != JournalEntryStatus.POSTED:
            raise LedgerReversalError(
                "Only posted journal entries can be reversed."
            )

        if JournalEntry.objects.filter(reversal_of=journal_entry).exists():
            raise LedgerReversalError(
                "This journal entry has already been reversed."
            )

        entry_lines = JournalLine.objects.select_related(
            "ledger_account",
        ).filter(
            journal_entry=journal_entry,
        )

        reverse_lines: list[JournalLineInput] = []

        for line in entry_lines:
            reverse_lines.append(
                JournalLineInput(
                    ledger_account=line.ledger_account,
                    entry_side=ReversalLedgerService._get_reversed_side(
                        line.entry_side,
                    ),
                    amount=line.amount,
                    description=(
                        f"Reversal of {journal_entry.entry_number}"
                    ),
                    user=line.user,
                    wallet_reference=line.wallet_reference,
                    payment_intent_reference=(
                        line.payment_intent_reference
                    ),
                    related_object_type=line.related_object_type,
                    related_object_id=line.related_object_id,
                    metadata=dict(line.metadata),
                )
            )

        if not reverse_lines:
            raise LedgerReversalError(
                "Cannot reverse a journal entry with no lines."
            )

        reversal_reason = reason or (
            f"Reversal of {journal_entry.entry_number}"
        )

        reversal_metadata = {
            "reversal_of_entry_number": journal_entry.entry_number,
            **(metadata or {}),
        }

        reversal_entry = JournalPostingService.post_entry(
            website=journal_entry.website,
            entry_type=LedgerEntryType.PAYMENT_REVERSAL,
            lines=reverse_lines,
            currency=journal_entry.currency,
            description=reversal_reason,
            reference=journal_entry.reference,
            source_app=journal_entry.source_app,
            source_model=journal_entry.source_model,
            source_object_id=journal_entry.source_object_id,
            external_reference=journal_entry.external_reference,
            payment_intent_reference=(
                journal_entry.payment_intent_reference
            ),
            triggered_by=triggered_by,
            reversal_of=journal_entry,
            metadata=reversal_metadata,
        )

        journal_entry.mark_reversed()
        journal_entry.save(
            update_fields=[
                "status",
                "updated_at",
            ],
        )

        return reversal_entry