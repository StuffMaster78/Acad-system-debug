from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from ledger.constants import EntrySide, JournalEntryStatus
from ledger.exceptions import LedgerPostingError
from ledger.models.journal_entry import JournalEntry
from ledger.models.journal_line import JournalLine
from ledger.models.ledger_account import LedgerAccount


@dataclass(frozen=True)
class JournalLineInput:
    """
    Immutable input used to build journal lines for a journal entry.
    """

    ledger_account: LedgerAccount
    entry_side: str
    amount: Decimal
    description: str = ""
    user: Any | None = None
    wallet_reference: str = ""
    payment_intent_reference: str = ""
    related_object_type: str = ""
    related_object_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class JournalPostingService:
    """
    Create and post balanced journal entries atomically.
    """

    @staticmethod
    def _validate_lines(
        *,
        website,
        currency: str,
        lines: list[JournalLineInput],
    ) -> None:
        """
        Validate line inputs before persisting a journal entry.
        """
        if not lines:
            raise LedgerPostingError(
                "Journal entry must have at least one line."
            )

        debit_total = Decimal("0.00")
        credit_total = Decimal("0.00")

        for line in lines:
            if line.amount <= Decimal("0.00"):
                raise LedgerPostingError(
                    "Journal line amount must be greater than zero."
                )

            if line.ledger_account.website.id != website.id:
                raise LedgerPostingError(
                    "All ledger accounts must belong to the same website."
                )

            if line.ledger_account.currency != currency:
                raise LedgerPostingError(
                    "All ledger accounts must match the journal currency."
                )

            if line.entry_side == EntrySide.DEBIT:
                debit_total += line.amount
            elif line.entry_side == EntrySide.CREDIT:
                credit_total += line.amount
            else:
                raise LedgerPostingError(
                    f"Invalid entry side: {line.entry_side}."
                )

        if debit_total != credit_total:
            raise LedgerPostingError(
                "Unbalanced entry. "
                f"Debits={debit_total}, Credits={credit_total}."
            )

    @staticmethod
    def _build_entry_number(*, website) -> str:
        """
        Build a unique human-readable entry number.
        """
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
        return f"JE-{website.id}-{timestamp}"

    @staticmethod
    @transaction.atomic
    def create_draft_entry(
        *,
        website,
        entry_type: str,
        currency: str = "USD",
        description: str = "",
        reference: str = "",
        source_app: str = "",
        source_model: str = "",
        source_object_id: str = "",
        external_reference: str = "",
        payment_intent_reference: str = "",
        triggered_by=None,
        approved_by=None,
        reversal_of=None,
        effective_at=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Create a draft journal entry before lines are attached.
        """
        return JournalEntry.objects.create(
            website=website,
            entry_number=JournalPostingService._build_entry_number(
                website=website,
            ),
            entry_type=entry_type,
            status=JournalEntryStatus.DRAFT,
            currency=currency,
            description=description,
            reference=reference,
            source_app=source_app,
            source_model=source_model,
            source_object_id=source_object_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            approved_by=approved_by,
            reversal_of=reversal_of,
            effective_at=effective_at or timezone.now(),
            metadata=metadata or {},
        )

    @staticmethod
    @transaction.atomic
    def add_lines(
        *,
        journal_entry: JournalEntry,
        lines: list[JournalLineInput],
    ) -> list[JournalLine]:
        """
        Persist journal lines for a draft journal entry.
        """
        created_lines: list[JournalLine] = []

        for line in lines:
            created_line = JournalLine.objects.create(
                website=journal_entry.website,
                journal_entry=journal_entry,
                ledger_account=line.ledger_account,
                entry_side=line.entry_side,
                amount=line.amount,
                currency=journal_entry.currency,
                description=line.description,
                user=line.user,
                wallet_reference=line.wallet_reference,
                payment_intent_reference=line.payment_intent_reference,
                related_object_type=line.related_object_type,
                related_object_id=line.related_object_id,
                metadata=dict(line.metadata),
            )
            created_lines.append(created_line)

        return created_lines

    @staticmethod
    @transaction.atomic
    def post_entry(
        *,
        website,
        entry_type: str,
        lines: list[JournalLineInput],
        currency: str = "USD",
        description: str = "",
        reference: str = "",
        source_app: str = "",
        source_model: str = "",
        source_object_id: str = "",
        external_reference: str = "",
        payment_intent_reference: str = "",
        triggered_by=None,
        approved_by=None,
        reversal_of=None,
        effective_at=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Validate, create, populate, and post a journal entry.
        """
        JournalPostingService._validate_lines(
            website=website,
            currency=currency,
            lines=lines,
        )

        entry = JournalPostingService.create_draft_entry(
            website=website,
            entry_type=entry_type,
            currency=currency,
            description=description,
            reference=reference,
            source_app=source_app,
            source_model=source_model,
            source_object_id=source_object_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            approved_by=approved_by,
            reversal_of=reversal_of,
            effective_at=effective_at,
            metadata=metadata,
        )

        JournalPostingService.add_lines(
            journal_entry=entry,
            lines=lines,
        )

        entry.mark_posted()
        entry.full_clean()
        entry.save(
            update_fields=[
                "status",
                "posted_at",
                "failure_reason",
                "updated_at",
            ],
        )

        return entry

    @staticmethod
    @transaction.atomic
    def fail_entry(
        *,
        entry: JournalEntry,
        reason: str,
    ) -> JournalEntry:
        """
        Mark an entry as failed with a failure reason.
        """
        entry.status = JournalEntryStatus.FAILED
        entry.failure_reason = reason
        entry.save(
            update_fields=[
                "status",
                "failure_reason",
                "updated_at",
            ],
        )
        return entry