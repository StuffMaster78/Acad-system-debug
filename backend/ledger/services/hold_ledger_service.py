from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from ledger.constants import HoldStatus
from ledger.exceptions import LedgerHoldError
from ledger.models.hold_record import HoldRecord
from ledger.models.ledger_account import LedgerAccount


class HoldLedgerService:
    """
    Handle fund reservations before final capture or release.
    """

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        """
        Validate that a hold amount is positive.
        """
        if amount <= Decimal("0.00"):
            raise LedgerHoldError(
                "Hold amount must be greater than zero."
            )

    @staticmethod
    def _validate_account_context(
        *,
        website,
        ledger_account: LedgerAccount,
        currency: str,
    ) -> None:
        """
        Validate tenant and currency consistency for a hold account.
        """
        if ledger_account.website.id != website.id:
            raise LedgerHoldError(
                "Ledger account must belong to the same website."
            )

        if ledger_account.currency != currency:
            raise LedgerHoldError(
                "Ledger account currency must match hold currency."
            )

    @staticmethod
    @transaction.atomic
    def create_hold(
        *,
        website,
        ledger_account: LedgerAccount,
        amount: Decimal,
        currency: str = "USD",
        user=None,
        journal_entry=None,
        reference: str = "",
        reason: str = "",
        wallet_reference: str = "",
        payment_intent_reference: str = "",
        related_object_type: str = "",
        related_object_id: str = "",
        expires_at=None,
        metadata: dict[str, Any] | None = None,
    ) -> HoldRecord:
        """
        Create a new active hold record.
        """
        HoldLedgerService._validate_amount(amount)
        HoldLedgerService._validate_account_context(
            website=website,
            ledger_account=ledger_account,
            currency=currency,
        )

        return HoldRecord.objects.create(
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

    @staticmethod
    @transaction.atomic
    def release_hold(*, hold: HoldRecord) -> HoldRecord:
        """
        Release an active hold.
        """
        if hold.status != HoldStatus.ACTIVE:
            raise LedgerHoldError(
                "Only active holds can be released."
            )

        hold.mark_released()
        hold.save(
            update_fields=[
                "status",
                "released_at",
                "updated_at",
            ],
        )
        return hold

    @staticmethod
    @transaction.atomic
    def capture_hold(*, hold: HoldRecord) -> HoldRecord:
        """
        Capture an active hold.
        """
        if hold.status != HoldStatus.ACTIVE:
            raise LedgerHoldError(
                "Only active holds can be captured."
            )

        hold.mark_captured()
        hold.save(
            update_fields=[
                "status",
                "captured_at",
                "updated_at",
            ],
        )
        return hold

    @staticmethod
    @transaction.atomic
    def cancel_hold(*, hold: HoldRecord) -> HoldRecord:
        """
        Cancel a non-final hold.
        """
        if hold.is_final:
            raise LedgerHoldError(
                "Final holds cannot be cancelled."
            )

        hold.mark_cancelled()
        hold.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_at",
            ],
        )
        return hold

    @staticmethod
    @transaction.atomic
    def expire_hold(*, hold: HoldRecord) -> HoldRecord:
        """
        Expire a non-final hold.
        """
        if hold.is_final:
            raise LedgerHoldError(
                "Final holds cannot be expired."
            )

        hold.mark_expired()
        hold.save(
            update_fields=[
                "status",
                "updated_at",
            ],
        )
        return hold

    @staticmethod
    def get_active_holds_total(
        *,
        website,
        wallet_reference: str,
        currency: str = "USD",
    ) -> Decimal:
        """
        Return the total amount of active holds for a wallet reference.
        """
        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        total = (
            HoldRecord.objects.filter(
                website=website,
                wallet_reference=wallet_reference,
                currency=currency,
                status=HoldStatus.ACTIVE,
            ).aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00"))
            )["total"]
        )
        return total