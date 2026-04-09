from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce

from ledger.constants import (
    CREDIT_NORMAL_ACCOUNT_TYPES,
    DEBIT_NORMAL_ACCOUNT_TYPES,
    EntrySide,
    JournalEntryStatus,
)
from ledger.models.ledger_account import  LedgerAccount
from ledger.models.account_balance_snapshot import AccountBalanceSnapshot
from ledger.models.journal_line import JournalLine


class BalanceService:
    """
    Computes balances from posted journal lines.
    """

    @staticmethod
    def get_account_balance(*, account: LedgerAccount) -> Decimal:
        debit_total = (
            JournalLine.objects.filter(
                ledger_account=account,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.DEBIT,
            )
            .aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))
            ["total"]
        )

        credit_total = (
            JournalLine.objects.filter(
                ledger_account=account,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.CREDIT,
            )
            .aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))
            ["total"]
        )

        if account.account_type in DEBIT_NORMAL_ACCOUNT_TYPES:
            return debit_total - credit_total

        if account.account_type in CREDIT_NORMAL_ACCOUNT_TYPES:
            return credit_total - debit_total

        return debit_total - credit_total

    @staticmethod
    def create_snapshot(
        *,
        account: LedgerAccount,
        reference: str = "",
        metadata: dict | None = None,
    ) -> AccountBalanceSnapshot:
        balance = BalanceService.get_account_balance(account=account)

        return AccountBalanceSnapshot.objects.create(
            website=account.website,
            ledger_account=account,
            currency=account.currency,
            balance=balance,
            reference=reference,
            metadata=metadata or {},
        )

    @staticmethod
    def get_user_wallet_balance(
        *,
        website,
        wallet_reference: str,
        currency: str = "KES",
    ) -> Decimal:
        debit_total = (
            JournalLine.objects.filter(
                website=website,
                wallet_reference=wallet_reference,
                currency=currency,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.DEBIT,
            )
            .aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))
            ["total"]
        )

        credit_total = (
            JournalLine.objects.filter(
                website=website,
                wallet_reference=wallet_reference,
                currency=currency,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.CREDIT,
            )
            .aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))
            ["total"]
        )

        return credit_total - debit_total