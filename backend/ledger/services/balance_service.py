from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Sum
from django.db.models.functions import Coalesce

from ledger.constants import (
    CREDIT_NORMAL_ACCOUNT_TYPES,
    DEBIT_NORMAL_ACCOUNT_TYPES,
    EntrySide,
    JournalEntryStatus,
)
from ledger.models.account_balance_snapshot import AccountBalanceSnapshot
from ledger.models.journal_line import JournalLine
from ledger.models.ledger_account import LedgerAccount
from ledger.services.account_service import AccountService


class BalanceService:
    """
    Compute balances from posted journal lines.
    """

    @staticmethod
    def _sum_lines(
        *,
        account: LedgerAccount,
        entry_side: str,
        extra_filters: dict[str, Any] | None = None,
    ) -> Decimal:
        """
        Sum posted journal line amounts for an account and entry side.
        """
        filters: dict[str, Any] = {
            "ledger_account": account,
            "journal_entry__status": JournalEntryStatus.POSTED,
            "entry_side": entry_side,
        }

        if extra_filters:
            filters.update(extra_filters)

        total = (
            JournalLine.objects.filter(**filters).aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00")),
            )["total"]
        )
        return total

    @staticmethod
    def get_account_balance(*, account: LedgerAccount) -> Decimal:
        """
        Return the posted balance for a ledger account.
        """
        debit_total = BalanceService._sum_lines(
            account=account,
            entry_side=EntrySide.DEBIT,
        )
        credit_total = BalanceService._sum_lines(
            account=account,
            entry_side=EntrySide.CREDIT,
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
        metadata: dict[str, Any] | None = None,
    ) -> AccountBalanceSnapshot:
        """
        Create a balance snapshot for a ledger account.
        """
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
    def get_client_wallet_balance(
        *,
        website,
        wallet_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return client wallet stored value balance.

        This balance is computed only from the client platform credit
        account, not from every line carrying the wallet reference.
        """
        client_credit = AccountService.get_system_account(
            website=website,
            key="client_platform_credit",
        )

        debit_total = BalanceService._sum_lines(
            account=client_credit,
            entry_side=EntrySide.DEBIT,
            extra_filters={
                "website": website,
                "wallet_reference": wallet_reference,
                "currency": currency,
            },
        )
        credit_total = BalanceService._sum_lines(
            account=client_credit,
            entry_side=EntrySide.CREDIT,
            extra_filters={
                "website": website,
                "wallet_reference": wallet_reference,
                "currency": currency,
            },
        )

        return credit_total - debit_total

    @staticmethod
    def get_writer_payable_balance(
        *,
        website,
        writer_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return writer payable balance for a writer reference.
        """
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )

        debit_total = BalanceService._sum_lines(
            account=writer_payable,
            entry_side=EntrySide.DEBIT,
            extra_filters={
                "website": website,
                "wallet_reference": writer_reference,
                "currency": currency,
            },
        )
        credit_total = BalanceService._sum_lines(
            account=writer_payable,
            entry_side=EntrySide.CREDIT,
            extra_filters={
                "website": website,
                "wallet_reference": writer_reference,
                "currency": currency,
            },
        )

        return credit_total - debit_total

    @staticmethod
    def get_writer_tip_payable_balance(
        *,
        website,
        writer_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return writer tip payable balance for a writer reference.
        """
        writer_tip_payable = AccountService.get_system_account(
            website=website,
            key="writer_tip_payable",
        )

        debit_total = BalanceService._sum_lines(
            account=writer_tip_payable,
            entry_side=EntrySide.DEBIT,
            extra_filters={
                "website": website,
                "wallet_reference": writer_reference,
                "currency": currency,
            },
        )
        credit_total = BalanceService._sum_lines(
            account=writer_tip_payable,
            entry_side=EntrySide.CREDIT,
            extra_filters={
                "website": website,
                "wallet_reference": writer_reference,
                "currency": currency,
            },
        )

        return credit_total - debit_total
    

    @staticmethod
    def get_writer_recovery_balance(
        *,
        website,
        writer_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return writer recovery balance for a writer reference.
        """
        writer_recovery = AccountService.get_system_account(
            website=website,
            key="writer_recovery",
        )

        debit_total = BalanceService._sum_lines(
            account=writer_recovery,
            entry_side=EntrySide.DEBIT,
            extra_filters={
                "website": website,
                "wallet_reference": writer_reference,
                "currency": currency,
            },
        )
        credit_total = BalanceService._sum_lines(
            account=writer_recovery,
            entry_side=EntrySide.CREDIT,
            extra_filters={
                "website": website,
                "wallet_reference": writer_reference,
                "currency": currency,
            },
        )

        return credit_total - debit_total