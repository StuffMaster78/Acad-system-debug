from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from audit_logging.services.audit_log_service import AuditLogService
from ledger.constants import JournalEntryStatus
from ledger.models.journal_line import JournalLine
from wallets.constants import WalletHoldStatus
from wallets.exceptions import WalletReconciliationError
from wallets.models import Wallet, WalletEntry, WalletHold


@dataclass
class WalletReconciliationResult:
    wallet_id: int
    website_id: int
    currency: str
    wallet_type: str

    actual_available_balance: Decimal
    actual_pending_balance: Decimal
    actual_total_balance: Decimal

    expected_available_balance_from_entries: Decimal
    expected_pending_balance_from_holds: Decimal
    expected_total_balance_from_ledger: Decimal

    available_balance_matches_entries: bool
    pending_balance_matches_holds: bool
    total_balance_matches_ledger: bool

    entry_chain_is_consistent: bool
    entry_chain_errors: list[str]

    active_hold_total: Decimal
    latest_entry_id: int | None

    ledger_account_code: str | None
    checked_at: Any


class WalletReconciliationService:
    """
    Reconciles wallet state against three sources:

    1. WalletEntry chain
       Used to validate available balance continuity for wallet-local activity.

    2. Active WalletHold rows
       Used to validate pending balance.

    3. Ledger journal lines
       Used to validate total wallet liability projection.

    Important:
    Ledger usually reflects the platform liability to the wallet owner, so the
    ledger comparison is made against:

        available_balance + pending_balance

    not just available_balance.
    """

    @staticmethod
    def _decimal(value: Decimal | None) -> Decimal:
        return value if value is not None else Decimal("0.00")

    @staticmethod
    def _wallet_total_balance(*, wallet: Wallet) -> Decimal:
        return wallet.available_balance + wallet.pending_balance

    @staticmethod
    def _get_latest_entry(*, wallet: Wallet) -> WalletEntry | None:
        return (
            WalletEntry.objects.filter(wallet=wallet)
            .order_by("-created_at", "-id")
            .first()
        )

    @staticmethod
    def _wallet_liability_account_code(*, wallet_type: str) -> str:
        if wallet_type == "client":
            return "CLIENT_WALLET_LIABILITY"

        if wallet_type == "writer":
            return "WRITER_WALLET_LIABILITY"

        raise WalletReconciliationError(
            f"Unsupported wallet type for reconciliation: {wallet_type}"
        )

    @staticmethod
    def get_active_hold_total(*, wallet: Wallet) -> Decimal:
        aggregate = WalletHold.objects.filter(
            wallet=wallet,
            status=WalletHoldStatus.ACTIVE,
        ).aggregate(total=Sum("amount"))

        return WalletReconciliationService._decimal(
            cast(Any, aggregate).get("total")
        )

    @staticmethod
    def get_expected_pending_balance_from_holds(*, wallet: Wallet) -> Decimal:
        return WalletReconciliationService.get_active_hold_total(wallet=wallet)

    @staticmethod
    def get_expected_available_balance_from_latest_entry(
        *,
        wallet: Wallet,
    ) -> Decimal:
        latest_entry = WalletReconciliationService._get_latest_entry(wallet=wallet)
        if latest_entry is None:
            return Decimal("0.00")
        return latest_entry.balance_after

    @staticmethod
    def get_expected_total_balance_from_ledger(*, wallet: Wallet) -> Decimal:
        """
        Computes net liability for this wallet from posted journal lines.

        debit decreases liability
        credit increases liability

        Net liability = credits - debits
        """

        account_code = WalletReconciliationService._wallet_liability_account_code(
            wallet_type=wallet.wallet_type
        )

        base_queryset = JournalLine.objects.filter(
            website=wallet.website,
            journal_entry__status=JournalEntryStatus.POSTED,
            ledger_account__code=account_code,
            ledger_account__currency=wallet.currency,
            wallet_reference=str(wallet.pk),
        )

        debit_total = WalletReconciliationService._decimal(
            cast(
                Any,
                base_queryset.filter(entry_side="debit").aggregate(
                    total=Sum("amount")
                ),
            ).get("total")
        )

        credit_total = WalletReconciliationService._decimal(
            cast(
                Any,
                base_queryset.filter(entry_side="credit").aggregate(
                    total=Sum("amount")
                ),
            ).get("total")
        )

        return credit_total - debit_total

    @staticmethod
    def validate_entry_chain(*, wallet: Wallet) -> tuple[bool, list[str]]:
        entries = list(
            WalletEntry.objects.filter(wallet=wallet).order_by("created_at", "id")
        )

        if not entries:
            return True, []

        errors: list[str] = []
        previous_after: Decimal | None = None
        previous_entry_id: int | None = None

        for entry in entries:
            if entry.amount <= Decimal("0.00"):
                errors.append(
                    f"Entry {cast(Any, entry).id} has non positive amount "
                    f"{entry.amount}."
                )

            if previous_after is not None and entry.balance_before != previous_after:
                errors.append(
                    "Entry chain break between "
                    f"{previous_entry_id} and {cast(Any, entry).id}: "
                    f"expected balance_before {previous_after}, "
                    f"got {entry.balance_before}."
                )

            previous_after = entry.balance_after
            previous_entry_id = cast(Any, entry).id

        return len(errors) == 0, errors

    @staticmethod
    def reconcile_wallet(*, wallet: Wallet) -> WalletReconciliationResult:
        expected_pending = (
            WalletReconciliationService.get_expected_pending_balance_from_holds(
                wallet=wallet
            )
        )
        expected_available = (
            WalletReconciliationService.get_expected_available_balance_from_latest_entry(
                wallet=wallet
            )
        )
        expected_total_from_ledger = (
            WalletReconciliationService.get_expected_total_balance_from_ledger(
                wallet=wallet
            )
        )

        entry_chain_is_consistent, entry_chain_errors = (
            WalletReconciliationService.validate_entry_chain(wallet=wallet)
        )
        latest_entry = WalletReconciliationService._get_latest_entry(wallet=wallet)
        active_hold_total = WalletReconciliationService.get_active_hold_total(
            wallet=wallet
        )

        actual_available = wallet.available_balance
        actual_pending = wallet.pending_balance
        actual_total = WalletReconciliationService._wallet_total_balance(wallet=wallet)

        return WalletReconciliationResult(
            wallet_id=cast(Any, wallet).id,
            website_id=cast(Any, wallet).website_id,
            currency=wallet.currency,
            wallet_type=wallet.wallet_type,
            actual_available_balance=actual_available,
            actual_pending_balance=actual_pending,
            actual_total_balance=actual_total,
            expected_available_balance_from_entries=expected_available,
            expected_pending_balance_from_holds=expected_pending,
            expected_total_balance_from_ledger=expected_total_from_ledger,
            available_balance_matches_entries=(
                actual_available == expected_available
            ),
            pending_balance_matches_holds=(
                actual_pending == expected_pending
            ),
            total_balance_matches_ledger=(
                actual_total == expected_total_from_ledger
            ),
            entry_chain_is_consistent=entry_chain_is_consistent,
            entry_chain_errors=entry_chain_errors,
            active_hold_total=active_hold_total,
            latest_entry_id=cast(Any, latest_entry).id if latest_entry else None,
            ledger_account_code=(
                WalletReconciliationService._wallet_liability_account_code(
                    wallet_type=wallet.wallet_type
                )
            ),
            checked_at=timezone.now(),
        )

    @staticmethod
    def wallet_has_drift(*, wallet: Wallet) -> bool:
        result = WalletReconciliationService.reconcile_wallet(wallet=wallet)
        return not (
            result.available_balance_matches_entries
            and result.pending_balance_matches_holds
            and result.total_balance_matches_ledger
            and result.entry_chain_is_consistent
        )

    @staticmethod
    def reconcile_website_wallets(*, website: Any) -> list[WalletReconciliationResult]:
        wallets = Wallet.objects.filter(website=website).select_related("website")
        return [
            WalletReconciliationService.reconcile_wallet(wallet=wallet)
            for wallet in wallets
        ]

    @staticmethod
    def get_wallets_with_drift(*, website: Any | None = None) -> list[Wallet]:
        queryset = Wallet.objects.all()

        if website is not None:
            queryset = queryset.filter(website=website)

        drifted_wallets: list[Wallet] = []
        for wallet in queryset.iterator():
            if WalletReconciliationService.wallet_has_drift(wallet=wallet):
                drifted_wallets.append(wallet)

        return drifted_wallets

    @staticmethod
    @transaction.atomic
    def repair_wallet_balances(
        *,
        wallet: Wallet,
        repaired_by: Any | None = None,
        reason: str = "Wallet reconciliation repair",
    ) -> WalletReconciliationResult:
        """
        Repairs wallet cached balances using:
        - latest wallet entry for available balance
        - active holds for pending balance

        Important:
        This method does NOT rewrite ledger.
        It repairs wallet projection state only.
        """

        locked_wallet = Wallet.objects.select_for_update().get(
            id=cast(Any, wallet).id
        )

        result_before = WalletReconciliationService.reconcile_wallet(
            wallet=locked_wallet
        )

        if not result_before.entry_chain_is_consistent:
            raise WalletReconciliationError(
                "Cannot repair wallet with inconsistent entry chain."
            )

        old_available = locked_wallet.available_balance
        old_pending = locked_wallet.pending_balance

        locked_wallet.available_balance = (
            result_before.expected_available_balance_from_entries
        )
        locked_wallet.pending_balance = (
            result_before.expected_pending_balance_from_holds
        )
        locked_wallet.last_activity_at = timezone.now()
        locked_wallet.save(
            update_fields=[
                "available_balance",
                "pending_balance",
                "last_activity_at",
                "updated_at",
            ]
        )

        try:
            cast(Any, AuditLogService).log_action(
                action="wallet.reconciliation.repaired",
                actor=repaired_by,
                target=locked_wallet,
                website=locked_wallet.website,
                metadata={
                    "wallet_id": cast(Any, locked_wallet).id,
                    "reason": reason,
                    "old_available_balance": str(old_available),
                    "new_available_balance": str(locked_wallet.available_balance),
                    "old_pending_balance": str(old_pending),
                    "new_pending_balance": str(locked_wallet.pending_balance),
                    "ledger_expected_total_balance": str(
                        result_before.expected_total_balance_from_ledger
                    ),
                },
            )
        except Exception:
            pass

        return WalletReconciliationService.reconcile_wallet(wallet=locked_wallet)

    @staticmethod
    def get_summary_for_website(*, website: Any) -> dict[str, Any]:
        results = WalletReconciliationService.reconcile_website_wallets(
            website=website
        )

        drifted_wallets = [
            result
            for result in results
            if not (
                result.available_balance_matches_entries
                and result.pending_balance_matches_holds
                and result.total_balance_matches_ledger
                and result.entry_chain_is_consistent
            )
        ]

        return {
            "website_id": website.id,
            "total_wallets": len(results),
            "drifted_wallets_count": len(drifted_wallets),
            "healthy_wallets_count": len(results) - len(drifted_wallets),
            "drifted_wallet_ids": [result.wallet_id for result in drifted_wallets],
            "checked_at": timezone.now(),
        }