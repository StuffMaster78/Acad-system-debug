from __future__ import annotations

from decimal import Decimal
from typing import Any

from ledger.constants import EntrySide, LedgerEntryType, SourceApp
from ledger.services.account_service import AccountService
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)


class PayoutLedgerService:
    """
    Posts writer earnings, payouts, and fines.
    """

    @staticmethod
    def post_writer_earning(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        related_object_type: str,
        related_object_id: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        platform_revenue = AccountService.get_system_account(
            website=website,
            key="platform_revenue",
        )
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )

        lines = [
            JournalLineInput(
                ledger_account=platform_revenue,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=writer_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_EARNING_ACCRUAL,
            lines=lines,
            description="Writer earning accrued.",
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model=related_object_type,
            source_object_id=related_object_id,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )

    @staticmethod
    def post_writer_payout(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        payout_id: str,
        external_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        platform_cash = AccountService.get_system_account(
            website=website,
            key="platform_cash",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=writer_reference,
                related_object_type="WriterPayment",
                related_object_id=payout_id,
            ),
            JournalLineInput(
                ledger_account=platform_cash,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
                related_object_type="WriterPayment",
                related_object_id=payout_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_PAYOUT,
            lines=lines,
            description="Writer payout recorded.",
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model="WriterPayment",
            source_object_id=payout_id,
            external_reference=external_reference,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )

    @staticmethod
    def post_writer_fine(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        fine_id: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        fines_recovery = AccountService.get_system_account(
            website=website,
            key="fines_recovery",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=writer_reference,
                related_object_type="Fine",
                related_object_id=fine_id,
            ),
            JournalLineInput(
                ledger_account=fines_recovery,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
                related_object_type="Fine",
                related_object_id=fine_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_FINE,
            lines=lines,
            description="Writer fine recorded.",
            source_app=SourceApp.FINES,
            source_model="Fine",
            source_object_id=fine_id,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )