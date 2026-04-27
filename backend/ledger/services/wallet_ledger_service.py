from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from ledger.constants import EntrySide, LedgerEntryType, SourceApp
from ledger.models import JournalEntry
from ledger.services.account_service import AccountService
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)


class WalletLedgerService:
    """
    Handle client stored value flows.

    Wallet credit is internal platform value.
    Revenue is not recognized here.
    """

    DEFAULT_CURRENCY = "USD"
    ZERO = Decimal("0.00")

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate that an amount is positive.
        """
        if amount <= WalletLedgerService.ZERO:
            raise ValueError("Amount must be greater than zero.")

    @staticmethod
    def _merge_metadata(
        *,
        base: dict[str, Any] | None,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge metadata without mutating caller-provided dictionaries.
        """
        return {
            **extra,
            **(base or {}),
        }

    @staticmethod
    @transaction.atomic
    def post_wallet_top_up(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        payment_intent_reference: str = "",
        external_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Record wallet top up.

        Accounting:
            Dr Platform Cash
            Cr Client Platform Credit
        """
        WalletLedgerService._validate_amount(amount=amount)

        platform_cash = AccountService.get_system_account(
            website=website,
            key="platform_cash",
        )
        client_credit = AccountService.get_system_account(
            website=website,
            key="client_platform_credit",
        )

        lines = [
            JournalLineInput(
                ledger_account=platform_cash,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description="Wallet top-up cash received.",
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                metadata={
                    "external_reference": external_reference,
                },
            ),
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description="Client wallet credited.",
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                metadata={
                    "external_reference": external_reference,
                },
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_TOP_UP,
            lines=lines,
            currency=WalletLedgerService.DEFAULT_CURRENCY,
            description="Client wallet top up recorded.",
            reference=payment_intent_reference or wallet_reference,
            source_app=SourceApp.WALLETS,
            source_model="User",
            source_object_id=client_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=WalletLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "client_id": client_id,
                    "wallet_reference": wallet_reference,
                    "payment_intent_reference": (
                        payment_intent_reference
                    ),
                    "external_reference": external_reference,
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_wallet_spend(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        payment_intent_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Record wallet spend.

        Accounting:
            Dr Client Platform Credit
            Cr Client Credit Consumption
        """
        WalletLedgerService._validate_amount(amount=amount)

        client_credit = AccountService.get_system_account(
            website=website,
            key="client_platform_credit",
        )
        credit_consumption = AccountService.get_system_account(
            website=website,
            key="client_credit_consumption",
        )

        lines = [
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description="Client wallet value consumed.",
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
            JournalLineInput(
                ledger_account=credit_consumption,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description="Wallet consumption recorded.",
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_SPEND,
            lines=lines,
            currency=WalletLedgerService.DEFAULT_CURRENCY,
            description="Client wallet spend recorded.",
            reference=reference or wallet_reference,
            source_app=SourceApp.WALLETS,
            source_model=related_object_type,
            source_object_id=related_object_id,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=WalletLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "client_id": client_id,
                    "wallet_reference": wallet_reference,
                    "related_object_type": related_object_type,
                    "related_object_id": related_object_id,
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_support_wallet_credit(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        reason: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Record support wallet credit.

        Accounting:
            Dr Manual Adjustments
            Cr Client Platform Credit
        """
        WalletLedgerService._validate_amount(amount=amount)

        manual_adjustments = AccountService.get_system_account(
            website=website,
            key="manual_adjustments",
        )
        client_credit = AccountService.get_system_account(
            website=website,
            key="client_platform_credit",
        )

        lines = [
            JournalLineInput(
                ledger_account=manual_adjustments,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
                wallet_reference=wallet_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=wallet_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_SUPPORT_CREDIT,
            lines=lines,
            currency=WalletLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=reference or wallet_reference,
            source_app=SourceApp.ADMIN,
            source_model=related_object_type,
            source_object_id=related_object_id,
            triggered_by=triggered_by,
            metadata=WalletLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "client_id": client_id,
                    "wallet_reference": wallet_reference,
                    "adjustment_direction": "credit",
                    "related_object_type": related_object_type,
                    "related_object_id": related_object_id,
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_support_wallet_debit(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        reason: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Record support wallet debit.

        Accounting:
            Dr Client Platform Credit
            Cr Manual Adjustments
        """
        WalletLedgerService._validate_amount(amount=amount)

        client_credit = AccountService.get_system_account(
            website=website,
            key="client_platform_credit",
        )
        manual_adjustments = AccountService.get_system_account(
            website=website,
            key="manual_adjustments",
        )

        lines = [
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
                wallet_reference=wallet_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
            JournalLineInput(
                ledger_account=manual_adjustments,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=wallet_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_SUPPORT_DEBIT,
            lines=lines,
            currency=WalletLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=reference or wallet_reference,
            source_app=SourceApp.ADMIN,
            source_model=related_object_type,
            source_object_id=related_object_id,
            triggered_by=triggered_by,
            metadata=WalletLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "client_id": client_id,
                    "wallet_reference": wallet_reference,
                    "adjustment_direction": "debit",
                    "related_object_type": related_object_type,
                    "related_object_id": related_object_id,
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_wallet_refund(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        refund_id: str,
        reason: str = "Refund credited to client wallet.",
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Record internal wallet refund.

        Accounting:
            Dr Manual Adjustments
            Cr Client Platform Credit
        """
        WalletLedgerService._validate_amount(amount=amount)

        manual_adjustments = AccountService.get_system_account(
            website=website,
            key="manual_adjustments",
        )
        client_credit = AccountService.get_system_account(
            website=website,
            key="client_platform_credit",
        )

        lines = [
            JournalLineInput(
                ledger_account=manual_adjustments,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
                wallet_reference=wallet_reference,
                related_object_type="Refund",
                related_object_id=refund_id,
            ),
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=wallet_reference,
                related_object_type="Refund",
                related_object_id=refund_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_REFUND,
            lines=lines,
            currency=WalletLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=reference or refund_id,
            source_app=SourceApp.REFUNDS,
            source_model="Refund",
            source_object_id=refund_id,
            triggered_by=triggered_by,
            metadata=WalletLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "client_id": client_id,
                    "wallet_reference": wallet_reference,
                    "refund_id": refund_id,
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_wallet_tip_deduction(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        writer_id: str,
        tip_reference: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Deduct wallet value for a tip.

        Accounting:
            Dr Client Platform Credit
            Cr Tip Allocation Clearing
        """
        WalletLedgerService._validate_amount(amount=amount)

        client_credit = AccountService.get_system_account(
            website=website,
            key="client_platform_credit",
        )
        tip_clearing = AccountService.get_system_account(
            website=website,
            key="tip_allocation_clearing",
        )

        lines = [
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description="Client wallet tip deducted.",
                wallet_reference=wallet_reference,
                related_object_type="Tip",
                related_object_id=tip_reference,
            ),
            JournalLineInput(
                ledger_account=tip_clearing,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description="Tip moved to allocation clearing.",
                wallet_reference=wallet_reference,
                related_object_type="Tip",
                related_object_id=tip_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_TIP_DEDUCTION,
            lines=lines,
            currency=WalletLedgerService.DEFAULT_CURRENCY,
            description="Client wallet tip deduction recorded.",
            reference=tip_reference,
            source_app=SourceApp.WALLETS,
            source_model="Tip",
            source_object_id=tip_reference,
            triggered_by=triggered_by,
            metadata=WalletLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "client_id": client_id,
                    "writer_id": writer_id,
                    "wallet_reference": wallet_reference,
                    "tip_reference": tip_reference,
                },
            ),
        )

    @staticmethod
    def post_cancellation_wallet_credit(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        reason: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Business-friendly wrapper for cancellation wallet credit.
        """
        return WalletLedgerService.post_support_wallet_credit(
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
    def post_dispute_wallet_refund(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        refund_id: str,
        reason: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Business-friendly wrapper for dispute wallet refund.
        """
        return WalletLedgerService.post_wallet_refund(
            website=website,
            amount=amount,
            wallet_reference=wallet_reference,
            client_id=client_id,
            refund_id=refund_id,
            reason=reason,
            reference=reference,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    @staticmethod
    def post_extra_service_wallet_debit(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        client_id: str,
        reason: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Business-friendly wrapper for extra service wallet debit.
        """
        return WalletLedgerService.post_support_wallet_debit(
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