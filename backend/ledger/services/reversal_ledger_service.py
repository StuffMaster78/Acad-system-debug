from __future__ import annotations

from typing import Any, cast

from django.db import transaction

from audit_logging.services.audit_log_service import AuditLogService
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

    Rules:
        1. Only posted entries can be reversed.
        2. Reversal entries cannot be reversed.
        3. An entry can only be reversed once.
        4. Reversal entries stay within the same tenant.
        5. Reversal lines use opposite debit or credit sides.
    """

    @staticmethod
    def _get_reversed_side(entry_side: str) -> str:
        """
        Return the opposite journal side.
        """
        if entry_side == EntrySide.DEBIT:
            return EntrySide.CREDIT

        if entry_side == EntrySide.CREDIT:
            return EntrySide.DEBIT

        raise LedgerReversalError(
            f"Invalid journal entry side: {entry_side}."
        )

    @staticmethod
    def _ensure_can_reverse_locked(*, journal_entry: JournalEntry) -> None:
        """
        Validate that a locked journal entry can be reversed.
        """
        if journal_entry.status != JournalEntryStatus.POSTED:
            raise LedgerReversalError(
                "Only posted journal entries can be reversed."
            )

        if getattr(journal_entry, "reversal_of_id", None) is not None:
            raise LedgerReversalError(
                "Cannot reverse a reversal entry."
            )

        already_reversed = JournalEntry.objects.filter(
            website=journal_entry.website,
            reversal_of=journal_entry,
        ).exists()

        if already_reversed:
            raise LedgerReversalError(
                "This journal entry has already been reversed."
            )

    @staticmethod
    def _build_reversal_lines(
        *,
        journal_entry: JournalEntry,
    ) -> list[JournalLineInput]:
        """
        Build compensating reversal lines from original journal lines.
        """
        entry_lines = JournalLine.objects.select_related(
            "ledger_account",
            "user",
        ).filter(
            website=journal_entry.website,
            journal_entry=journal_entry,
        )

        reverse_lines: list[JournalLineInput] = []

        for line in entry_lines:
            if (
                getattr(line.ledger_account, "website_id", None)
                != getattr(journal_entry, "website_id", None)
            ):
                raise LedgerReversalError(
                    "Journal line account does not belong to the "
                    "journal entry website."
                )

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
                    metadata={
                        **(line.metadata or {}),
                        "reversed_line_id": str(cast(Any, line).id),
                        "reversed_entry_number": (
                            journal_entry.entry_number
                        ),
                    },
                )
            )

        if not reverse_lines:
            raise LedgerReversalError(
                "Cannot reverse a journal entry with no lines."
            )

        return reverse_lines

    @staticmethod
    def _log_reversal(
        *,
        original_entry: JournalEntry,
        reversal_entry: JournalEntry,
        triggered_by: Any | None,
        metadata: dict[str, Any],
    ) -> None:
        """
        Best-effort audit log for reversal operations.
        """
        try:
            cast(Any, AuditLogService).log_action(
                action="ledger.entry.reversed",
                actor=triggered_by,
                target=original_entry,
                website=original_entry.website,
                metadata={
                    **metadata,
                    "original_entry_id": str(cast(Any, original_entry).id),
                    "original_entry_number": original_entry.entry_number,
                    "reversal_entry_id": str(cast(Any, reversal_entry).id),
                    "reversal_entry_number": reversal_entry.entry_number,
                },
            )
        except Exception:
            pass

    @staticmethod
    @transaction.atomic
    def reverse_entry(
        *,
        journal_entry: JournalEntry,
        triggered_by: Any | None = None,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Reverse a posted journal entry by creating a compensating entry.
        """
        locked_entry = JournalEntry.objects.select_for_update().get(
            id=cast(Any, journal_entry).id,
            website=journal_entry.website,
        )

        ReversalLedgerService._ensure_can_reverse_locked(
            journal_entry=locked_entry,
        )

        reverse_lines = ReversalLedgerService._build_reversal_lines(
            journal_entry=locked_entry,
        )

        reversal_reason = reason or (
            f"Reversal of {locked_entry.entry_number}"
        )

        reversal_metadata = {
            **(metadata or {}),
            "reversal_of_entry_id": str(cast(Any, locked_entry).id),
            "reversal_of_entry_number": locked_entry.entry_number,
            "reversal_reason": reversal_reason,
        }

        reversal_entry = JournalPostingService.post_entry(
            website=locked_entry.website,
            entry_type=LedgerEntryType.REVERSAL,
            lines=reverse_lines,
            currency=locked_entry.currency,
            description=reversal_reason,
            reference=locked_entry.reference,
            source_app=locked_entry.source_app,
            source_model=locked_entry.source_model,
            source_object_id=locked_entry.source_object_id,
            external_reference=locked_entry.external_reference,
            payment_intent_reference=(
                locked_entry.payment_intent_reference
            ),
            triggered_by=triggered_by,
            reversal_of=locked_entry,
            metadata=reversal_metadata,
        )

        locked_entry.mark_reversed()
        locked_entry.save(
            update_fields=[
                "status",
                "updated_at",
            ],
        )

        ReversalLedgerService._log_reversal(
            original_entry=locked_entry,
            reversal_entry=reversal_entry,
            triggered_by=triggered_by,
            metadata=reversal_metadata,
        )

        return reversal_entry