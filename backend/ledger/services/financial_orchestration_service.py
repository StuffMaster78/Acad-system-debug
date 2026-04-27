from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction

from ledger.services.balance_service import BalanceService
from ledger.services.payment_processor_ledger_service import (
    PaymentProcessorLedgerService,
)
from ledger.services.wallet_ledger_service import WalletLedgerService
from ledger.services.writer_ledger_service import WriterLedgerService


@dataclass(frozen=True)
class TipSplit:
    """
    Represent a wallet-funded tip split between writer and platform.
    """

    total_tip_amount: Decimal
    writer_share: Decimal
    platform_share: Decimal


class FinancialOrchestrationService:
    """
    Coordinate multi-step financial ledger flows.

    Domain apps decide the business outcome first.
    This service only coordinates matching ledger effects.
    """

    ZERO = Decimal("0")

    @staticmethod
    def _validate_amount(amount: Decimal, field_name: str) -> None:
        """
        Validate that an amount is positive.
        """
        if amount <= FinancialOrchestrationService.ZERO:
            raise ValueError(f"{field_name} must be greater than zero.")

    @staticmethod
    def _validate_optional_positive_amount(
        amount: Decimal | None,
        field_name: str,
    ) -> None:
        """
        Validate optional amount only when supplied.
        """
        if amount is not None and amount < FinancialOrchestrationService.ZERO:
            raise ValueError(f"{field_name} cannot be negative.")

    @staticmethod
    def _validate_tip_split(tip_split: TipSplit) -> None:
        """
        Validate that a tip split is internally consistent.
        """
        FinancialOrchestrationService._validate_amount(
            tip_split.total_tip_amount,
            "total_tip_amount",
        )
        FinancialOrchestrationService._validate_amount(
            tip_split.writer_share,
            "writer_share",
        )

        if tip_split.platform_share < FinancialOrchestrationService.ZERO:
            raise ValueError("platform_share cannot be negative.")

        if (
            tip_split.writer_share + tip_split.platform_share
            != tip_split.total_tip_amount
        ):
            raise ValueError(
                "writer_share plus platform_share must equal "
                "total_tip_amount."
            )

    @staticmethod
    def _merge_metadata(
        *,
        base: dict[str, Any] | None,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge metadata safely without mutating caller-provided dictionaries.
        """
        return {
            **(base or {}),
            **extra,
        }

    @staticmethod
    @transaction.atomic
    def tip_writer_from_wallet(
        *,
        website: Any,
        wallet_reference: str,
        client_id: str,
        writer_reference: str,
        writer_id: str,
        tip_split: TipSplit,
        tip_reference: str,
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Deduct a client wallet tip and allocate it to writer and platform.
        """
        FinancialOrchestrationService._validate_tip_split(tip_split)

        WalletLedgerService.post_wallet_tip_deduction(
            website=website,
            amount=tip_split.total_tip_amount,
            wallet_reference=wallet_reference,
            client_id=client_id,
            writer_id=writer_id,
            tip_reference=tip_reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

        return WriterLedgerService.post_writer_tip_credit(
            website=website,
            total_tip_amount=tip_split.total_tip_amount,
            writer_share=tip_split.writer_share,
            platform_share=tip_split.platform_share,
            writer_reference=writer_reference,
            writer_id=writer_id,
            tip_reference=tip_reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def refund_client_to_wallet(
        *,
        website: Any,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        refund_id: str,
        reason: str,
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Refund a client internally by crediting wallet value.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WalletLedgerService.post_dispute_wallet_refund(
            website=website,
            amount=amount,
            wallet_reference=wallet_reference,
            client_id=client_id,
            refund_id=refund_id,
            reason=reason,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def refund_client_externally(
        *,
        website: Any,
        amount: Decimal,
        refund_id: str,
        payment_intent_reference: str,
        external_reference: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Refund a client externally through the payment processor.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return PaymentProcessorLedgerService.post_external_refund(
            website=website,
            amount=amount,
            refund_id=refund_id,
            payment_intent_reference=payment_intent_reference,
            external_reference=external_reference,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def support_cancel_and_credit_wallet(
        *,
        website: Any,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        reason: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Credit wallet after cancellation or support-approved restoration.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WalletLedgerService.post_cancellation_wallet_credit(
            website=website,
            amount=amount,
            wallet_reference=wallet_reference,
            client_id=client_id,
            reason=reason,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def support_debit_wallet_for_service(
        *,
        website: Any,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        reason: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Debit wallet for a support-mediated extra service or charge.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WalletLedgerService.post_extra_service_wallet_debit(
            website=website,
            amount=amount,
            wallet_reference=wallet_reference,
            client_id=client_id,
            reason=reason,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def accrue_writer_earning(
        *,
        website: Any,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Accrue writer earnings after a valid earning event is confirmed.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WriterLedgerService.post_writer_earning_accrual(
            website=website,
            amount=amount,
            writer_reference=writer_reference,
            writer_id=writer_id,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def apply_writer_bonus(
        *,
        website: Any,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Apply a bonus to writer payable.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WriterLedgerService.post_writer_bonus(
            website=website,
            amount=amount,
            writer_reference=writer_reference,
            writer_id=writer_id,
            reason=reason,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def apply_writer_fine(
        *,
        website: Any,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        fine_id: str,
        reason: str,
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Apply a fine that reduces writer payable.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WriterLedgerService.post_writer_fine(
            website=website,
            amount=amount,
            writer_reference=writer_reference,
            writer_id=writer_id,
            fine_id=fine_id,
            reason=reason,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def increase_writer_balance(
        *,
        website: Any,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Increase writer balance through a manual adjustment.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WriterLedgerService.post_writer_earning_restoration(
            website=website,
            amount=amount,
            writer_reference=writer_reference,
            writer_id=writer_id,
            reason=reason,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def decrease_writer_balance(
        *,
        website: Any,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Decrease writer balance through a manual adjustment.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WriterLedgerService.post_writer_earning_recovery(
            website=website,
            amount=amount,
            writer_reference=writer_reference,
            writer_id=writer_id,
            reason=reason,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def payout_writer(
        *,
        website: Any,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        payout_id: str,
        external_reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Post a writer payout after payout execution is confirmed.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WriterLedgerService.post_writer_payout(
            website=website,
            amount=amount,
            writer_reference=writer_reference,
            writer_id=writer_id,
            payout_id=payout_id,
            external_reference=external_reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def resolve_dispute_for_client_with_wallet_refund(
        *,
        website: Any,
        refund_amount: Decimal,
        wallet_reference: str,
        client_id: str,
        refund_id: str,
        refund_reason: str,
        writer_recovery_amount: Decimal | None = None,
        writer_reference: str = "",
        writer_id: str = "",
        writer_recovery_reason: str = "",
        writer_recovery_reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Resolve a client-winning dispute with a wallet refund and optional
        writer recovery.
        """
        FinancialOrchestrationService._validate_amount(
            refund_amount,
            "refund_amount",
        )
        FinancialOrchestrationService._validate_optional_positive_amount(
            writer_recovery_amount,
            "writer_recovery_amount",
        )

        wallet_refund_entry = WalletLedgerService.post_dispute_wallet_refund(
            website=website,
            amount=refund_amount,
            wallet_reference=wallet_reference,
            client_id=client_id,
            refund_id=refund_id,
            reason=refund_reason,
            triggered_by=triggered_by,
            metadata=metadata,
        )

        writer_recovery_entry = None
        if writer_recovery_amount and writer_recovery_amount > Decimal("0"):
            writer_recovery_entry = (
                WriterLedgerService.post_writer_earning_recovery(
                    website=website,
                    amount=writer_recovery_amount,
                    writer_reference=writer_reference,
                    writer_id=writer_id,
                    reason=writer_recovery_reason,
                    reference=writer_recovery_reference,
                    triggered_by=triggered_by,
                    metadata=metadata,
                )
            )

        return {
            "wallet_refund_entry": wallet_refund_entry,
            "writer_recovery_entry": writer_recovery_entry,
        }

    @staticmethod
    @transaction.atomic
    def resolve_dispute_for_client_with_external_refund(
        *,
        website: Any,
        refund_amount: Decimal,
        refund_id: str,
        payment_intent_reference: str,
        external_reference: str,
        related_object_type: str,
        related_object_id: str,
        writer_recovery_amount: Decimal | None = None,
        writer_reference: str = "",
        writer_id: str = "",
        writer_recovery_reason: str = "",
        writer_recovery_reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Resolve a client-winning dispute with an external refund and
        optional writer recovery.
        """
        FinancialOrchestrationService._validate_amount(
            refund_amount,
            "refund_amount",
        )
        FinancialOrchestrationService._validate_optional_positive_amount(
            writer_recovery_amount,
            "writer_recovery_amount",
        )

        external_refund_entry = (
            PaymentProcessorLedgerService.post_external_refund(
                website=website,
                amount=refund_amount,
                refund_id=refund_id,
                payment_intent_reference=payment_intent_reference,
                external_reference=external_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
                triggered_by=triggered_by,
                metadata=metadata,
            )
        )

        writer_recovery_entry = None
        if writer_recovery_amount and writer_recovery_amount > Decimal("0"):
            writer_recovery_entry = (
                WriterLedgerService.post_writer_earning_recovery(
                    website=website,
                    amount=writer_recovery_amount,
                    writer_reference=writer_reference,
                    writer_id=writer_id,
                    reason=writer_recovery_reason,
                    reference=writer_recovery_reference,
                    triggered_by=triggered_by,
                    metadata=metadata,
                )
            )

        return {
            "external_refund_entry": external_refund_entry,
            "writer_recovery_entry": writer_recovery_entry,
        }

    @staticmethod
    @transaction.atomic
    def restore_writer_after_dispute_win(
        *,
        website: Any,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Restore writer balance after dispute resolution in writer's favor.
        """
        FinancialOrchestrationService._validate_amount(amount, "amount")

        return WriterLedgerService.post_writer_earning_restoration(
            website=website,
            amount=amount,
            writer_reference=writer_reference,
            writer_id=writer_id,
            reason=reason,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def settle_writer_payout(
        *,
        website: Any,
        writer_reference: str,
        writer_id: str,
        payout_id: str,
        gross_payout_amount: Decimal,
        external_reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Settle a writer payout by applying outstanding recovery first,
        then posting cash payout for the net amount.
        """
        FinancialOrchestrationService._validate_amount(
            gross_payout_amount,
            "gross_payout_amount",
        )

        recovery_balance = BalanceService.get_writer_recovery_balance(
            website=website,
            writer_reference=writer_reference,
        )

        recovery_to_apply = min(gross_payout_amount, recovery_balance)
        net_payout_amount = gross_payout_amount - recovery_to_apply

        recovery_entry = None
        payout_entry = None

        if recovery_to_apply > Decimal("0"):
            recovery_entry = (
                WriterLedgerService.post_writer_recovery_applied_to_payout(
                    website=website,
                    amount=recovery_to_apply,
                    writer_reference=writer_reference,
                    writer_id=writer_id,
                    payout_id=payout_id,
                    triggered_by=triggered_by,
                    metadata=metadata,
                )
            )

        if net_payout_amount > Decimal("0"):
            payout_entry = WriterLedgerService.post_writer_payout(
                website=website,
                amount=net_payout_amount,
                writer_reference=writer_reference,
                writer_id=writer_id,
                payout_id=payout_id,
                external_reference=external_reference,
                triggered_by=triggered_by,
                metadata=FinancialOrchestrationService._merge_metadata(
                    base=metadata,
                    extra={
                        "gross_payout_amount": str(gross_payout_amount),
                        "recovery_applied": str(recovery_to_apply),
                        "net_payout_amount": str(net_payout_amount),
                    },
                ),
            )

        return {
            "gross_payout_amount": gross_payout_amount,
            "recovery_balance": recovery_balance,
            "recovery_applied": recovery_to_apply,
            "net_payout_amount": net_payout_amount,
            "recovery_entry": recovery_entry,
            "payout_entry": payout_entry,
        }