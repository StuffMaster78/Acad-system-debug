from __future__ import annotations

from typing import Any, cast

from django.db import transaction
from django.db.models.manager import RelatedManager

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

    Important:
        The original posted journal entry remains POSTED.

        Accounting reversals are represented by a new posted compensating
        entry linked through reversal_of.
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
        locked_entry = (
            JournalEntry.objects.select_for_update()
            .select_related("website", "reversal_of")
            .get(pk=journal_entry.pk)
        )

        if locked_entry.status != JournalEntryStatus.POSTED:
            raise LedgerReversalError(
                "Only posted journal entries can be reversed."
            )

        if locked_entry.reversal_of is not None:
            raise LedgerReversalError(
                "A reversal entry cannot itself be reversed."
            )

        reversal_exists = JournalEntry.objects.filter(
            reversal_of=locked_entry,
            status=JournalEntryStatus.POSTED,
        ).exists()

        if reversal_exists:
            raise LedgerReversalError(
                "This journal entry has already been reversed."
            )

        line_manager = cast(
            RelatedManager[JournalLine],
            getattr(locked_entry, "lines"),
        )

        original_lines = list(
            line_manager.select_related("ledger_account")
        )

        if not original_lines:
            raise LedgerReversalError(
                "Cannot reverse a journal entry without lines."
            )

        reversal_lines = [
            JournalLineInput(
                ledger_account=line.ledger_account,
                entry_side=ReversalLedgerService._get_reversed_side(
                    line.entry_side
                ),
                amount=line.amount,
                description=(
                    f"Reversal of line {line.pk}: "
                    f"{line.description or ''}"
                ),
                metadata={
                    "reversed_line_id": str(line.pk),
                    **(line.metadata or {}),
                },
            )
            for line in original_lines
        ]

        reversal_metadata = {
            "reversed_entry_id": str(locked_entry.pk),
            "reversal_reason": reason,
            **(metadata or {}),
        }

        reversal_entry = JournalPostingService.post_entry(
            website=locked_entry.website,
            entry_type=LedgerEntryType.REVERSAL,
            description=(
                f"Reversal of journal entry {locked_entry.pk}. {reason}"
            ).strip(),
            lines=reversal_lines,
            triggered_by=triggered_by,
            reference=f"REVERSAL-{locked_entry.pk}",
            metadata=reversal_metadata,
            reversal_of=locked_entry,
        )

        return reversal_entry