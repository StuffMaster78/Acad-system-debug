from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

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
    Compute tenant-scoped ledger balances from posted journal lines.

    Important:
        This service reads accounting truth only.
        It does not mutate journal entries or wallet balances.
    """

    @staticmethod
    def _decimal_zero() -> Decimal:
        return Decimal("0")

    @staticmethod
    def _sum_lines(
        *,
        account: LedgerAccount,
        entry_side: str,
        extra_filters: dict[str, Any] | None = None,
    ) -> Decimal:
        """
        Sum posted journal line amounts for one ledger account and side.
        """
        filters: dict[str, Any] = {
            "website": account.website,
            "ledger_account": account,
            "journal_entry__status": JournalEntryStatus.POSTED,
            "entry_side": entry_side,
            "currency": account.currency,
        }

        if extra_filters:
            filters.update(extra_filters)

        total = (
            JournalLine.objects.filter(**filters).aggregate(
                total=Coalesce(
                    Sum("amount"),
                    BalanceService._decimal_zero(),
                ),
            )["total"]
        )

        return cast(Decimal, total)

    @staticmethod
    def _credit_normal_balance(
        *,
        account: LedgerAccount,
        wallet_reference: str,
        currency: str,
    ) -> Decimal:
        """
        Return credits minus debits for a credit-normal account.
        """
        debit_total = BalanceService._sum_lines(
            account=account,
            entry_side=EntrySide.DEBIT,
            extra_filters={
                "wallet_reference": wallet_reference,
                "currency": currency,
            },
        )
        credit_total = BalanceService._sum_lines(
            account=account,
            entry_side=EntrySide.CREDIT,
            extra_filters={
                "wallet_reference": wallet_reference,
                "currency": currency,
            },
        )

        return credit_total - debit_total

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
        website: Any,
        wallet_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return client wallet liability balance for a wallet reference.
        """
        client_wallet_liability = AccountService.get_system_account(
            website=website,
            key="client_wallet_liability",
        )

        return BalanceService._credit_normal_balance(
            account=client_wallet_liability,
            wallet_reference=wallet_reference,
            currency=currency,
        )

    @staticmethod
    def get_writer_wallet_balance(
        *,
        website: Any,
        writer_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return writer wallet liability balance for a writer wallet reference.
        """
        writer_wallet_liability = AccountService.get_system_account(
            website=website,
            key="writer_wallet_liability",
        )

        return BalanceService._credit_normal_balance(
            account=writer_wallet_liability,
            wallet_reference=writer_reference,
            currency=currency,
        )

    @staticmethod
    def get_writer_payable_balance(
        *,
        website: Any,
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

        return BalanceService._credit_normal_balance(
            account=writer_payable,
            wallet_reference=writer_reference,
            currency=currency,
        )

    @staticmethod
    def get_writer_tip_payable_balance(
        *,
        website: Any,
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

        return BalanceService._credit_normal_balance(
            account=writer_tip_payable,
            wallet_reference=writer_reference,
            currency=currency,
        )

    @staticmethod
    def get_writer_recovery_balance(
        *,
        website: Any,
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

        return BalanceService._credit_normal_balance(
            account=writer_recovery,
            wallet_reference=writer_reference,
            currency=currency,
        )