from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.utils import timezone

from audit_logging.services.audit_log_service import AuditLogService
from wallets.constants import (
    WalletEntryDirection,
    WalletEntryStatus,
    WalletEntryType,
    WalletHoldStatus,
)
from wallets.exceptions import WalletHoldError
from wallets.models import Wallet, WalletEntry, WalletHold
from wallets.services.wallet_service import WalletService


class WalletHoldService:
    """
    Handles wallet holds lifecycle:
        create -> release | capture | expire

    Rules:
        - Always tenant-safe
        - Always atomic
        - Always balance-consistent
    """

    # ---------------------------
    # Helpers
    # ---------------------------

    @staticmethod
    def _get_hold_for_update(*, hold_id: int) -> WalletHold:
        return (
            WalletHold.objects.select_for_update()
            .select_related("wallet", "website")
            .get(id=hold_id)
        )

    @staticmethod
    def _validate_positive_amount(amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise WalletHoldError("Amount must be greater than zero.")

    @staticmethod
    def _create_entry(
        *,
        website: Any,
        wallet: Wallet,
        entry_type: str,
        direction: str,
        amount: Decimal,
        available_before: Decimal,
        available_after: Decimal,
        pending_before: Decimal,
        pending_after: Decimal,
        description: str,
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WalletEntry:
        return WalletEntry.objects.create(
            website=website,
            wallet=wallet,
            entry_type=entry_type,
            direction=direction,
            status=WalletEntryStatus.POSTED,
            amount=amount,
            balance_before=available_before,
            balance_after=available_after,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            metadata={
                "pending_balance_before": str(pending_before),
                "pending_balance_after": str(pending_after),
                **(metadata or {}),
            },
            created_by=created_by,
        )

    @staticmethod
    def _log_audit(
        *,
        action: str,
        website: Any,
        actor: Any | None,
        hold: WalletHold,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        try:
            cast(Any, AuditLogService).log_action(
                action=action,
                actor=actor,
                target=hold.wallet,
                website=website,
                metadata={
                    "wallet_id": cast(Any, hold).wallet_id,
                    "wallet_hold_id": cast(Any, hold).id,
                    "amount": str(hold.amount),
                    "status": hold.status,
                    "reason": hold.reason,
                    **(metadata or {}),
                },
            )
        except Exception:
            pass

    # ---------------------------
    # Core Operations
    # ---------------------------

    @staticmethod
    @transaction.atomic
    def create_hold(
        *,
        wallet: Wallet,
        amount: Decimal,
        website: Any,
        reason: str,
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "",
        reference_id: str = "",
        expires_at: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletHold:

        if not reason.strip():
            raise WalletHoldError("Hold reason is required.")

        WalletHoldService._validate_positive_amount(amount)

        locked_wallet = WalletService.get_wallet_for_update(
            wallet_id=cast(Any, wallet).id
        )

        WalletService.assert_wallet_belongs_to_website(
            wallet=locked_wallet,
            website=website,
        )
        WalletService.assert_wallet_active(locked_wallet)

        available_before = locked_wallet.available_balance
        pending_before = locked_wallet.pending_balance

        if available_before < amount:
            raise WalletHoldError("Insufficient available balance.")

        # move funds
        locked_wallet.available_balance -= amount
        locked_wallet.pending_balance += amount
        locked_wallet.last_activity_at = timezone.now()
        locked_wallet.save(
            update_fields=[
                "available_balance",
                "pending_balance",
                "last_activity_at",
                "updated_at",
            ]
        )

        hold = WalletHold.objects.create(
            website=website,
            wallet=locked_wallet,
            amount=amount,
            status=WalletHoldStatus.ACTIVE,
            reason=reason,
            created_by=created_by,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        WalletHoldService._create_entry(
            website=website,
            wallet=locked_wallet,
            entry_type=WalletEntryType.HOLD,
            direction=WalletEntryDirection.DEBIT,
            amount=amount,
            available_before=available_before,
            available_after=locked_wallet.available_balance,
            pending_before=pending_before,
            pending_after=locked_wallet.pending_balance,
            description=f"Funds reserved: {reason}",
            created_by=created_by,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata={"wallet_hold_id": cast(Any, hold).id},
        )

        WalletHoldService._log_audit(
            action="wallet.hold.created",
            website=website,
            actor=created_by,
            hold=hold,
        )

        return hold

    @staticmethod
    @transaction.atomic
    def release_hold(
        *,
        hold: WalletHold,
        released_by: Any | None = None,
    ) -> WalletHold:

        locked_hold = WalletHoldService._get_hold_for_update(
            hold_id=cast(Any, hold).id
        )

        if locked_hold.status != WalletHoldStatus.ACTIVE:
            raise WalletHoldError("Only active holds can be released.")

        locked_wallet = WalletService.get_wallet_for_update(
            wallet_id=cast(Any, locked_hold).wallet_id
        )

        WalletService.assert_wallet_belongs_to_website(
            wallet=locked_wallet,
            website=locked_hold.website,
        )
        if getattr(locked_hold, "website_id", None) != getattr(locked_wallet, "website_id", None):
            raise WalletHoldError("Hold and wallet tenant mismatch.")

        available_before = locked_wallet.available_balance
        pending_before = locked_wallet.pending_balance

        if pending_before < locked_hold.amount:
            raise WalletHoldError("Corrupt pending balance.")

        # move funds back
        locked_wallet.available_balance += locked_hold.amount
        locked_wallet.pending_balance -= locked_hold.amount
        locked_wallet.save(
            update_fields=["available_balance", "pending_balance", "updated_at"]
        )

        locked_hold.status = WalletHoldStatus.RELEASED
        locked_hold.released_at = timezone.now()
        locked_wallet.last_activity_at = timezone.now()
        locked_hold.save(update_fields=["status", "released_at", "last_activity_at", "updated_at"])

        WalletHoldService._create_entry(
            website=locked_hold.website,
            wallet=locked_wallet,
            entry_type=WalletEntryType.HOLD_RELEASE,
            direction=WalletEntryDirection.CREDIT,
            amount=locked_hold.amount,
            available_before=available_before,
            available_after=locked_wallet.available_balance,
            pending_before=pending_before,
            pending_after=locked_wallet.pending_balance,
            description="Hold released",
            created_by=released_by,
            metadata={"wallet_hold_id": cast(Any, locked_hold).id}
        )

        WalletHoldService._log_audit(
            action="wallet.hold.released",
            website=locked_hold.website,
            actor=released_by,
            hold=locked_hold,
        )

        return locked_hold

    @staticmethod
    @transaction.atomic
    def capture_hold(
        *,
        hold: WalletHold,
        captured_by: Any | None = None,
    ) -> WalletHold:

        locked_hold = WalletHoldService._get_hold_for_update(
            hold_id=cast(Any, hold).id
        )

        if locked_hold.status != WalletHoldStatus.ACTIVE:
            raise WalletHoldError("Only active holds can be captured.")

        locked_wallet = WalletService.get_wallet_for_update(
            wallet_id=cast(Any, locked_hold).wallet_id
        )

        WalletService.assert_wallet_belongs_to_website(
            wallet=locked_wallet,
            website=locked_hold.website,
        )
        if getattr(locked_hold, "website_id", None) != getattr(locked_wallet, "website_id", None):
            raise WalletHoldError("Hold and wallet tenant mismatch.")

        pending_before = locked_wallet.pending_balance

        if pending_before < locked_hold.amount:
            raise WalletHoldError("Corrupt pending balance.")

        # consume pending funds
        locked_wallet.pending_balance -= locked_hold.amount
        locked_wallet.total_debited += locked_hold.amount
        locked_wallet.save(
            update_fields=["pending_balance", "total_debited", "updated_at"]
        )

        locked_hold.status = WalletHoldStatus.CAPTURED
        locked_hold.captured_at = timezone.now()
        locked_wallet.last_activity_at = timezone.now()
        locked_hold.save(update_fields=["status", "captured_at", "last_activity_at", "updated_at"])

        WalletHoldService._create_entry(
            website=locked_hold.website,
            wallet=locked_wallet,
            entry_type=WalletEntryType.HOLD_CAPTURE,
            direction=WalletEntryDirection.DEBIT,
            amount=locked_hold.amount,
            available_before=locked_wallet.available_balance,
            available_after=locked_wallet.available_balance,
            pending_before=pending_before,
            pending_after=locked_wallet.pending_balance,
            description="Hold captured",
            created_by=captured_by,
            metadata={"wallet_hold_id": cast(Any, locked_hold).id}
        )

        WalletHoldService._log_audit(
            action="wallet.hold.captured",
            website=locked_hold.website,
            actor=captured_by,
            hold=locked_hold,
        )

        return locked_hold