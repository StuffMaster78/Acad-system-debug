from __future__ import annotations

from decimal import Decimal
from typing import Any, cast
from django.utils import timezone

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from audit_logging.services.audit_log_service import AuditLogService
from ledger.constants import HoldStatus
from ledger.exceptions import LedgerHoldError
from ledger.models.hold_record import HoldRecord
from ledger.models.ledger_account import LedgerAccount

from ledger.services.balance_service import BalanceService

class HoldLedgerService:
    """
    Handle ledger-level fund reservations before final capture,
    release, cancellation, or expiry.

    Important:
        This service manages ledger hold records only.
        It does not mutate wallet balances directly.
    """

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        """
        Validate that a hold amount is positive.
        """
        if amount <= Decimal("0"):
            raise LedgerHoldError("Hold amount must be greater than zero.")

    @staticmethod
    def _validate_account_context(
        *,
        website: Any,
        ledger_account: LedgerAccount,
        currency: str,
    ) -> None:
        """
        Validate tenant and currency consistency for the ledger account.
        """
        account_website_id = getattr(ledger_account, "website_id", None)
        website_id = getattr(website, "id", None)

        if account_website_id != website_id:
            raise LedgerHoldError(
                "Ledger account must belong to the same website."
            )

        if ledger_account.currency != currency:
            raise LedgerHoldError(
                "Ledger account currency must match hold currency."
            )

    @staticmethod
    def _get_hold_for_update(*, hold_id: int) -> HoldRecord:
        """
        Lock a hold row before mutating it.

        This prevents race conditions such as release and capture
        happening at the same time.
        """
        return (
            HoldRecord.objects.select_for_update()
            .select_related("website", "ledger_account", "journal_entry", "user")
            .get(id=hold_id)
        )

    @staticmethod
    def _assert_hold_account_context(*, hold: HoldRecord) -> None:
        """
        Ensure the hold's ledger account still belongs to the hold tenant
        and uses the hold currency.
        """
        HoldLedgerService._validate_account_context(
            website=hold.website,
            ledger_account=hold.ledger_account,
            currency=hold.currency,
        )

    @staticmethod
    def _validate_expiry(expires_at: Any | None) -> None:
        """
        Ensure hold expiry is in the future.
        """
        if expires_at is None:
            return

        if expires_at <= timezone.now():
            raise LedgerHoldError(
                "Hold expiry must be in the future."
            )

    @staticmethod
    def _log_action(
        *,
        action: str,
        hold: HoldRecord,
        actor: Any | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Best-effort audit logging for ledger hold lifecycle changes.
        """
        try:
            cast(Any, AuditLogService).log_action(
                action=action,
                actor=actor or hold.user,
                target=hold,
                website=hold.website,
                metadata={
                    "hold_id": cast(Any, hold).id,
                    "ledger_account_id": getattr(
                        hold,
                        "ledger_account_id",
                        None,
                    ),
                    "journal_entry_id": getattr(
                        hold,
                        "journal_entry_id",
                        None,
                    ),
                    "amount": str(hold.amount),
                    "currency": hold.currency,
                    "status": hold.status,
                    "reference": hold.reference,
                    "wallet_reference": hold.wallet_reference,
                    "payment_intent_reference": (
                        hold.payment_intent_reference
                    ),
                    "related_object_type": hold.related_object_type,
                    "related_object_id": hold.related_object_id,
                    **(extra_metadata or {}),
                },
            )
        except Exception:
            pass

    @staticmethod
    @transaction.atomic
    def create_hold(
        *,
        website: Any,
        ledger_account: LedgerAccount,
        amount: Decimal,
        currency: str = "USD",
        user: Any | None = None,
        journal_entry: Any | None = None,
        reference: str = "",
        reason: str = "",
        wallet_reference: str = "",
        payment_intent_reference: str = "",
        related_object_type: str = "",
        related_object_id: str = "",
        expires_at: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> HoldRecord:
        """
        Create a new active ledger hold.

        The hold is tenant-scoped by website and tied to a tenant-scoped
        ledger account.
        """
        HoldLedgerService._validate_amount(amount)

        HoldLedgerService._validate_account_context(
            website=website,
            ledger_account=ledger_account,
            currency=currency,
        )

        HoldLedgerService._validate_expiry(expires_at)

        available_balance = BalanceService.get_available_balance(
            account=ledger_account,
            wallet_reference=wallet_reference,
        )

        if amount > available_balance:
            raise LedgerHoldError(
                "Insufficient available balance for hold."
            )

        hold = HoldRecord.objects.create(
            website=website,
            ledger_account=ledger_account,
            journal_entry=journal_entry,
            user=user,
            amount=amount,
            currency=currency,
            reference=reference,
            reason=reason,
            wallet_reference=wallet_reference,
            payment_intent_reference=payment_intent_reference,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        HoldLedgerService._log_action(
            action="ledger.hold.created",
            hold=hold,
            actor=user,
        )
        return hold
    
    @staticmethod
    def _raise_if_expired_active_hold(
        *,
        hold: HoldRecord,
    ) -> None:
        """
        Mark expired active holds as expired and block further mutation.
        """
        if hold.status != HoldStatus.ACTIVE:
            return

        if hold.expires_at is None:
            return

        if hold.expires_at > timezone.now():
            return

        hold.mark_expired()
        hold.save(
            update_fields=[
                "status",
                "updated_at",
            ],
        )

        raise LedgerHoldError("Hold has already expired.")

    @staticmethod
    @transaction.atomic
    def release_hold(
        *,
        hold: HoldRecord,
        released_by: Any | None = None,
    ) -> HoldRecord:
        """
        Release an active ledger hold.
        """
        locked_hold = HoldLedgerService._get_hold_for_update(
            hold_id=cast(Any, hold).id,
        )
        HoldLedgerService._assert_hold_account_context(hold=locked_hold)
        HoldLedgerService._raise_if_expired_active_hold(hold=locked_hold)

        if locked_hold.status != HoldStatus.ACTIVE:
            raise LedgerHoldError("Only active holds can be released.")

        locked_hold.mark_released()
        locked_hold.save(
            update_fields=[
                "status",
                "released_at",
                "updated_at",
            ],
        )

        HoldLedgerService._log_action(
            action="ledger.hold.released",
            hold=locked_hold,
            actor=released_by,
        )
        return locked_hold

    @staticmethod
    @transaction.atomic
    def capture_hold(
        *,
        hold: HoldRecord,
        captured_by: Any | None = None,
    ) -> HoldRecord:
        """
        Capture an active ledger hold.
        """
        locked_hold = HoldLedgerService._get_hold_for_update(
            hold_id=cast(Any, hold).id,
        )
        HoldLedgerService._assert_hold_account_context(hold=locked_hold)
        HoldLedgerService._raise_if_expired_active_hold(hold=locked_hold)

        if locked_hold.status != HoldStatus.ACTIVE:
            raise LedgerHoldError("Only active holds can be captured.")

        locked_hold.mark_captured()
        locked_hold.save(
            update_fields=[
                "status",
                "captured_at",
                "updated_at",
            ],
        )

        HoldLedgerService._log_action(
            action="ledger.hold.captured",
            hold=locked_hold,
            actor=captured_by,
        )
        return locked_hold

    @staticmethod
    @transaction.atomic
    def cancel_hold(
        *,
        hold: HoldRecord,
        cancelled_by: Any | None = None,
    ) -> HoldRecord:
        """
        Cancel a non-final ledger hold.
        """
        locked_hold = HoldLedgerService._get_hold_for_update(
            hold_id=cast(Any, hold).id,
        )
        HoldLedgerService._assert_hold_account_context(hold=locked_hold)
        HoldLedgerService._raise_if_expired_active_hold(hold=locked_hold)

        if locked_hold.is_final:
            raise LedgerHoldError("Final holds cannot be cancelled.")

        locked_hold.mark_cancelled()
        locked_hold.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_at",
            ],
        )

        HoldLedgerService._log_action(
            action="ledger.hold.cancelled",
            hold=locked_hold,
            actor=cancelled_by,
        )
        return locked_hold

    @staticmethod
    @transaction.atomic
    def expire_hold(
        *,
        hold: HoldRecord,
        expired_by: Any | None = None,
    ) -> HoldRecord:
        """
        Expire a non-final ledger hold.
        """
        locked_hold = HoldLedgerService._get_hold_for_update(
            hold_id=cast(Any, hold).id,
        )
        HoldLedgerService._assert_hold_account_context(hold=locked_hold)

        if locked_hold.is_final:
            raise LedgerHoldError("Final holds cannot be expired.")

        locked_hold.mark_expired()

        update_fields = [
            "status",
            "updated_at",
        ]

        if hasattr(locked_hold, "expired_at"):
            update_fields.append("expired_at")

        locked_hold.save(update_fields=update_fields)

        HoldLedgerService._log_action(
            action="ledger.hold.expired",
            hold=locked_hold,
            actor=expired_by,
        )
        return locked_hold

    @staticmethod
    def get_active_holds_total(
        *,
        website: Any,
        wallet_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return the total active ledger holds for a wallet reference.
        """
        total = (
            HoldRecord.objects.filter(
                website=website,
                wallet_reference=wallet_reference,
                currency=currency,
                status=HoldStatus.ACTIVE,
            ).aggregate(
                total=Coalesce(Sum("amount"), Decimal("0")),
            )["total"]
        )

        return cast(Decimal, total)