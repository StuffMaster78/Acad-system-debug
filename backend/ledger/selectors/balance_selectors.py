from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce

from ledger.constants import EntrySide, JournalEntryStatus
from ledger.models import AccountBalanceSnapshot, JournalLine, LedgerAccount


class BalanceSelectors:
    """
    Read only queries for balances and snapshots.
    """

    @staticmethod
    def get_latest_snapshot_for_account(
        *,
        account: LedgerAccount,
    ) -> AccountBalanceSnapshot | None:
        return (
            AccountBalanceSnapshot.objects.filter(
                website=account.website,
                ledger_account=account,
            )
            .order_by("-snapshot_date")
            .first()
        )

    @staticmethod
    def get_snapshots_for_account(
        *,
        account: LedgerAccount,
    ):
        return AccountBalanceSnapshot.objects.filter(
            website=account.website,
            ledger_account=account,
        ).order_by("-snapshot_date")

    @staticmethod
    def get_posted_debit_total_for_account(
        *,
        account: LedgerAccount,
    ) -> Decimal:
        total = (
            JournalLine.objects.filter(
                ledger_account=account,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.DEBIT,
            ).aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00"))
            )["total"]
        )
        return total

    @staticmethod
    def get_posted_credit_total_for_account(
        *,
        account: LedgerAccount,
    ) -> Decimal:
        total = (
            JournalLine.objects.filter(
                ledger_account=account,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.CREDIT,
            ).aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00"))
            )["total"]
        )
        return total

    @staticmethod
    def get_wallet_posted_debit_total(
        *,
        website,
        wallet_reference: str,
        currency: str = "KES",
    ) -> Decimal:
        total = (
            JournalLine.objects.filter(
                website=website,
                wallet_reference=wallet_reference,
                currency=currency,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.DEBIT,
            ).aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00"))
            )["total"]
        )
        return total

    @staticmethod
    def get_wallet_posted_credit_total(
        *,
        website,
        wallet_reference: str,
        currency: str = "KES",
    ) -> Decimal:
        total = (
            JournalLine.objects.filter(
                website=website,
                wallet_reference=wallet_reference,
                currency=currency,
                journal_entry__status=JournalEntryStatus.POSTED,
                entry_side=EntrySide.CREDIT,
            ).aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00"))
            )["total"]
        )
        return total