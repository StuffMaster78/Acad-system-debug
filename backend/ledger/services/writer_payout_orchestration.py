from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction

from ledger.services.balance_service import BalanceService
from ledger.services.writer_ledger_service import WriterLedgerService


@dataclass(frozen=True)
class WriterPayoutSettlementResult:
    """
    Result of settling a writer payout in the ledger.
    """

    payout_id: str
    writer_id: str
    gross_payout_amount: Decimal
    recovery_balance: Decimal
    recovery_applied: Decimal
    net_payout_amount: Decimal
    recovery_entry_id: str
    payout_entry_id: str


class WriterPayoutOrchestrationService:
    """
    Settle writer payout ledger effects.

    This service does not call payment providers directly.
    External payout execution should happen in payments_processor.
    """

    ZERO = Decimal("0.00")

    @staticmethod
    def _validate_amount(*, amount: Decimal, field_name: str) -> None:
        """
        Validate that an amount is positive.
        """
        if amount <= WriterPayoutOrchestrationService.ZERO:
            raise ValueError(f"{field_name} must be greater than zero.")

    @staticmethod
    def _get_recovery_to_apply(
        *,
        gross_payout_amount: Decimal,
        recovery_balance: Decimal,
    ) -> Decimal:
        """
        Return recovery amount to apply before payout.
        """
        if recovery_balance <= WriterPayoutOrchestrationService.ZERO:
            return WriterPayoutOrchestrationService.ZERO

        return min(gross_payout_amount, recovery_balance)

    @staticmethod
    def _merge_metadata(
        *,
        base: dict[str, Any] | None,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge metadata safely.
        """
        return {
            **extra,
            **(base or {}),
        }

    @classmethod
    @transaction.atomic
    def settle_writer_payout(
        cls,
        *,
        website,
        writer_reference: str,
        writer_id: str,
        payout_id: str,
        gross_payout_amount: Decimal,
        external_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> WriterPayoutSettlementResult:
        """
        Apply recovery first, then post the net writer payout.

        Flow:
            1. Check outstanding writer recovery.
            2. Apply recovery against payable.
            3. Post net payout only if cash should leave.
        """
        cls._validate_amount(
            amount=gross_payout_amount,
            field_name="gross_payout_amount",
        )

        recovery_balance = BalanceService.get_writer_recovery_balance(
            website=website,
            writer_reference=writer_reference,
        )

        recovery_applied = cls._get_recovery_to_apply(
            gross_payout_amount=gross_payout_amount,
            recovery_balance=recovery_balance,
        )

        net_payout_amount = gross_payout_amount - recovery_applied

        recovery_entry = None
        payout_entry = None

        if recovery_applied > cls.ZERO:
            recovery_entry = (
                WriterLedgerService.post_writer_recovery_applied_to_payout(
                    website=website,
                    amount=recovery_applied,
                    writer_reference=writer_reference,
                    writer_id=writer_id,
                    payout_id=payout_id,
                    reason="Writer recovery applied before payout.",
                    reference=payout_id,
                    triggered_by=triggered_by,
                    metadata=cls._merge_metadata(
                        base=metadata,
                        extra={
                            "gross_payout_amount": str(
                                gross_payout_amount,
                            ),
                            "recovery_applied": str(recovery_applied),
                            "net_payout_amount": str(net_payout_amount),
                        },
                    ),
                )
            )

        if net_payout_amount > cls.ZERO:
            payout_entry = WriterLedgerService.post_writer_payout(
                website=website,
                amount=net_payout_amount,
                writer_reference=writer_reference,
                writer_id=writer_id,
                payout_id=payout_id,
                external_reference=external_reference,
                triggered_by=triggered_by,
                metadata=cls._merge_metadata(
                    base=metadata,
                    extra={
                        "gross_payout_amount": str(gross_payout_amount),
                        "recovery_applied": str(recovery_applied),
                        "net_payout_amount": str(net_payout_amount),
                    },
                ),
            )

        return WriterPayoutSettlementResult(
            payout_id=payout_id,
            writer_id=writer_id,
            gross_payout_amount=gross_payout_amount,
            recovery_balance=recovery_balance,
            recovery_applied=recovery_applied,
            net_payout_amount=net_payout_amount,
            recovery_entry_id=(
                str(recovery_entry.id) if recovery_entry else ""
            ),
            payout_entry_id=str(payout_entry.id) if payout_entry else "",
        )