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
from wallets.constants import WalletHoldStatus, WalletType
from wallets.exceptions import WalletReconciliationError
from wallets.models import Wallet, WalletEntry, WalletHold


@dataclass(frozen=True)
class WalletReconciliationResult:
    """
    Immutable reconciliation report for one wallet.
    """

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
    Reconciles wallet cached state against wallet entries, active holds,
    and posted ledger journal lines.

    Sources of truth:
        WalletEntry:
            Expected available balance.

        WalletHold:
            Expected pending/held balance.

        Ledger:
            Expected total wallet liability.

    Important:
        This service must never infer tenant from a user.
        Tenant comes from wallet.website or an explicit website argument.
    """

    ENTRY_SIDE_DEBIT = "debit"
    ENTRY_SIDE_CREDIT = "credit"

    @staticmethod
    def _decimal(value: Decimal | None) -> Decimal:
        """
        Normalize nullable aggregate results to Decimal zero.
        """
        return value if value is not None else Decimal("0.00")

    @staticmethod
    def _wallet_total_balance(*, wallet: Wallet) -> Decimal:
        """
        Return the wallet's total projected balance.
        """
        return wallet.available_balance + wallet.pending_balance

    @staticmethod
    def _get_latest_entry(*, wallet: Wallet) -> WalletEntry | None:
        """
        Return the latest wallet entry for balance projection.
        """
        return (
            WalletEntry.objects.filter(
                wallet=wallet,
                website=wallet.website,
            )
            .order_by("-created_at", "-id")
            .first()
        )

    @staticmethod
    def _wallet_liability_account_code(*, wallet_type: str) -> str:
        """
        Resolve the ledger liability account for a wallet type.
        """
        if wallet_type == WalletType.CLIENT:
            return "CLIENT_WALLET_LIABILITY"

        if wallet_type == WalletType.WRITER:
            return "WRITER_WALLET_LIABILITY"

        raise WalletReconciliationError(
            f"Unsupported wallet type for reconciliation: {wallet_type}"
        )

    @staticmethod
    def _assert_wallet_belongs_to_website(
        *,
        wallet: Wallet,
        website: Any,
    ) -> None:
        """
        Ensure reconciliation is tenant safe.
        """
        if getattr(wallet, "website_id", None) != getattr(website, "id", None):
            raise WalletReconciliationError(
                "Wallet does not belong to the provided website."
            )

    @staticmethod
    def get_active_hold_total(*, wallet: Wallet) -> Decimal:
        """
        Sum active holds for this wallet.
        """
        aggregate = WalletHold.objects.filter(
            wallet=wallet,
            website=wallet.website,
            status=WalletHoldStatus.ACTIVE,
        ).aggregate(total=Sum("amount"))

        return WalletReconciliationService._decimal(
            cast(Any, aggregate).get("total"),
        )

    @staticmethod
    def get_expected_pending_balance_from_holds(*, wallet: Wallet) -> Decimal:
        """
        Return expected pending balance from active holds.
        """
        return WalletReconciliationService.get_active_hold_total(wallet=wallet)

    @staticmethod
    def get_expected_available_balance_from_latest_entry(
        *,
        wallet: Wallet,
    ) -> Decimal:
        """
        Return expected available balance from the latest wallet entry.
        """
        latest_entry = WalletReconciliationService._get_latest_entry(
            wallet=wallet,
        )

        if latest_entry is None:
            return Decimal("0.00")

        return latest_entry.balance_after

    @staticmethod
    def get_expected_total_balance_from_ledger(*, wallet: Wallet) -> Decimal:
        """
        Compute net wallet liability from posted journal lines.

        Debit decreases liability.
        Credit increases liability.

        Net liability = credits - debits.
        """
        account_code = (
            WalletReconciliationService._wallet_liability_account_code(
                wallet_type=wallet.wallet_type,
            )
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
                base_queryset.filter(
                    entry_side=WalletReconciliationService.ENTRY_SIDE_DEBIT,
                ).aggregate(total=Sum("amount")),
            ).get("total"),
        )

        credit_total = WalletReconciliationService._decimal(
            cast(
                Any,
                base_queryset.filter(
                    entry_side=WalletReconciliationService.ENTRY_SIDE_CREDIT,
                ).aggregate(total=Sum("amount")),
            ).get("total"),
        )

        return credit_total - debit_total

    @staticmethod
    def validate_entry_chain(*, wallet: Wallet) -> tuple[bool, list[str]]:
        """
        Validate that wallet entry balance_before/balance_after chain is intact.
        """
        entries = list(
            WalletEntry.objects.filter(
                wallet=wallet,
                website=wallet.website,
            ).order_by("created_at", "id"),
        )

        if not entries:
            return True, []

        errors: list[str] = []
        previous_after: Decimal | None = None
        previous_entry_id: int | None = None

        for entry in entries:
            entry_id = cast(Any, entry).id

            if entry.amount <= Decimal("0.00"):
                errors.append(
                    f"Entry {entry_id} has non-positive amount {entry.amount}."
                )

            if (
                previous_after is not None
                and entry.balance_before != previous_after
            ):
                errors.append(
                    "Entry chain break between "
                    f"{previous_entry_id} and {entry_id}: "
                    f"expected balance_before {previous_after}, "
                    f"got {entry.balance_before}."
                )

            previous_after = entry.balance_after
            previous_entry_id = entry_id

        return len(errors) == 0, errors

    @staticmethod
    def reconcile_wallet(*, wallet: Wallet) -> WalletReconciliationResult:
        """
        Reconcile one wallet and return a report.

        This method does not mutate state.
        """
        expected_pending = (
            WalletReconciliationService
            .get_expected_pending_balance_from_holds(wallet=wallet)
        )
        expected_available = (
            WalletReconciliationService
            .get_expected_available_balance_from_latest_entry(wallet=wallet)
        )
        expected_total_from_ledger = (
            WalletReconciliationService
            .get_expected_total_balance_from_ledger(wallet=wallet)
        )

        entry_chain_is_consistent, entry_chain_errors = (
            WalletReconciliationService.validate_entry_chain(wallet=wallet)
        )
        latest_entry = WalletReconciliationService._get_latest_entry(
            wallet=wallet,
        )
        active_hold_total = WalletReconciliationService.get_active_hold_total(
            wallet=wallet,
        )

        actual_available = wallet.available_balance
        actual_pending = wallet.pending_balance
        actual_total = WalletReconciliationService._wallet_total_balance(
            wallet=wallet,
        )

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
            latest_entry_id=(
                cast(Any, latest_entry).id if latest_entry is not None else None
            ),
            ledger_account_code=(
                WalletReconciliationService
                ._wallet_liability_account_code(
                    wallet_type=wallet.wallet_type,
                )
            ),
            checked_at=timezone.now(),
        )

    @staticmethod
    def wallet_has_drift(*, wallet: Wallet) -> bool:
        """
        Return whether wallet state differs from expected projections.
        """
        result = WalletReconciliationService.reconcile_wallet(wallet=wallet)

        return not (
            result.available_balance_matches_entries
            and result.pending_balance_matches_holds
            and result.total_balance_matches_ledger
            and result.entry_chain_is_consistent
        )

    @staticmethod
    def reconcile_website_wallets(
        *,
        website: Any,
    ) -> list[WalletReconciliationResult]:
        """
        Reconcile all wallets for a website.
        """
        wallets = Wallet.objects.filter(
            website=website,
        ).select_related("website")

        return [
            WalletReconciliationService.reconcile_wallet(wallet=wallet)
            for wallet in wallets
        ]

    @staticmethod
    def get_wallets_with_drift(*, website: Any) -> list[Wallet]:
        """
        Return drifted wallets for one tenant.

        Website is required intentionally. We do not support global drift scans
        here because this service should stay tenant explicit.
        """
        queryset = Wallet.objects.filter(website=website)

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
        Repair wallet cached balances from wallet-local projections.

        Repairs:
            available_balance from latest wallet entry
            pending_balance from active holds

        Does not:
            rewrite ledger
            rewrite wallet entries
        """
        locked_wallet = (
            Wallet.objects.select_for_update()
            .select_related("website")
            .get(id=cast(Any, wallet).id)
        )

        result_before = WalletReconciliationService.reconcile_wallet(
            wallet=locked_wallet,
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
            ],
        )

        WalletReconciliationService._log_repair_audit(
            repaired_by=repaired_by,
            wallet=locked_wallet,
            reason=reason,
            old_available=old_available,
            old_pending=old_pending,
            result_before=result_before,
        )

        return WalletReconciliationService.reconcile_wallet(
            wallet=locked_wallet,
        )

    @staticmethod
    def get_summary_for_website(*, website: Any) -> dict[str, Any]:
        """
        Return reconciliation health summary for one website.
        """
        results = WalletReconciliationService.reconcile_website_wallets(
            website=website,
        )

        drifted_results = [
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
            "drifted_wallets_count": len(drifted_results),
            "healthy_wallets_count": len(results) - len(drifted_results),
            "drifted_wallet_ids": [
                result.wallet_id for result in drifted_results
            ],
            "checked_at": timezone.now(),
        }

    @staticmethod
    def _log_repair_audit(
        *,
        repaired_by: Any | None,
        wallet: Wallet,
        reason: str,
        old_available: Decimal,
        old_pending: Decimal,
        result_before: WalletReconciliationResult,
    ) -> None:
        """
        Best-effort audit logging for wallet repair.
        """
        try:
            cast(Any, AuditLogService).log_action(
                action="wallet.reconciliation.repaired",
                actor=repaired_by,
                target=wallet,
                website=wallet.website,
                metadata={
                    "wallet_id": cast(Any, wallet).id,
                    "reason": reason,
                    "old_available_balance": str(old_available),
                    "new_available_balance": str(wallet.available_balance),
                    "old_pending_balance": str(old_pending),
                    "new_pending_balance": str(wallet.pending_balance),
                    "ledger_expected_total_balance": str(
                        result_before.expected_total_balance_from_ledger
                    ),
                },
            )
        except Exception:
            pass