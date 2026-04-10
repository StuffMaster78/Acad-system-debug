from __future__ import annotations

from decimal import Decimal
from typing import Any

from ledger.constants import EntrySide, LedgerEntryType, SourceApp
from ledger.services.account_service import AccountService
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)


class WalletLedgerService:
    """
    Handle client stored value flows.

    Important:
    - Wallet does not move platform cash directly
    - Wallet represents internal platform credit
    - Revenue is not recognized here
    """

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        """
        Validate that an amount is positive.
        """
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

    @staticmethod
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
    ):
        """
        Record wallet top up.

        This increases client stored value after money has already entered
        the platform.
        """
        WalletLedgerService._validate_amount(amount)

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
                wallet_reference=wallet_reference,
            ),
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=wallet_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_TOP_UP,
            lines=lines,
            description="Client wallet top up recorded.",
            source_app=SourceApp.WALLETS,
            source_model="User",
            source_object_id=client_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata={
                "client_id": client_id,
                **(metadata or {}),
            },
        )

    @staticmethod
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
    ):
        """
        Record wallet spend.

        This consumes client stored value and credits an internal
        consumption account. It does not recognize new revenue.
        """
        WalletLedgerService._validate_amount(amount)

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
                wallet_reference=wallet_reference,
            ),
            JournalLineInput(
                ledger_account=credit_consumption,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=wallet_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_SPEND,
            lines=lines,
            description="Client wallet spend recorded.",
            reference=reference,
            source_app=SourceApp.WALLETS,
            source_model=related_object_type,
            source_object_id=related_object_id,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata={
                "client_id": client_id,
                **(metadata or {}),
            },
        )

    @staticmethod
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
    ):
        """
        Record support credit to wallet.

        Used when support restores value to the client wallet after a
        cancellation, adjustment, or goodwill action.
        """
        WalletLedgerService._validate_amount(amount)

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
            ),
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_SUPPORT_CREDIT,
            lines=lines,
            description=reason,
            reference=reference,
            source_app=SourceApp.ADMIN,
            source_model=related_object_type,
            source_object_id=related_object_id,
            triggered_by=triggered_by,
            metadata={
                "client_id": client_id,
                "adjustment_direction": "credit",
                **(metadata or {}),
            },
        )

    @staticmethod
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
    ):
        """
        Record support debit from wallet.

        Used when support deducts client wallet value for an extra service
        or another agreed internal charge.
        """
        WalletLedgerService._validate_amount(amount)

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
            ),
            JournalLineInput(
                ledger_account=manual_adjustments,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_SUPPORT_DEBIT,
            lines=lines,
            description=reason,
            reference=reference,
            source_app=SourceApp.ADMIN,
            source_model=related_object_type,
            source_object_id=related_object_id,
            triggered_by=triggered_by,
            metadata={
                "client_id": client_id,
                "adjustment_direction": "debit",
                **(metadata or {}),
            },
        )

    @staticmethod
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
    ):
        """
        Record refund to wallet.

        This restores client stored value internally. It is used when the
        refund destination is wallet, not external processor.
        """
        WalletLedgerService._validate_amount(amount)

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
            ),
            JournalLineInput(
                ledger_account=client_credit,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_REFUND,
            lines=lines,
            description=reason,
            reference=reference or refund_id,
            source_app=SourceApp.REFUNDS,
            source_model="Refund",
            source_object_id=refund_id,
            triggered_by=triggered_by,
            metadata={
                "client_id": client_id,
                "refund_id": refund_id,
                **(metadata or {}),
            },
        )

    @staticmethod
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
    ):
        """
        Record wallet tip deduction.

        This deducts client stored value and moves the amount into tip
        allocation clearing for writer and platform distribution.
        """
        WalletLedgerService._validate_amount(amount)

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
            ),
            JournalLineInput(
                ledger_account=tip_clearing,
                entry_side=EntrySide.CREDIT,
                amount=amount,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.CLIENT_WALLET_TIP_DEDUCTION,
            lines=lines,
            description="Client wallet tip deduction recorded.",
            reference=tip_reference,
            source_app=SourceApp.WALLETS,
            source_model="Tip",
            source_object_id=tip_reference,
            triggered_by=triggered_by,
            metadata={
                "client_id": client_id,
                "writer_id": writer_id,
                **(metadata or {}),
            },
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
    ):
        """
        Record wallet credit after cancellation.

        This is a business-friendly wrapper around support wallet credit.
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
    ):
        """
        Record dispute refund to wallet.

        This is a business-friendly wrapper for wallet refund after a
        dispute is resolved for the client.
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
    ):
        """
        Record wallet debit for extra service.

        This is a business-friendly wrapper around support wallet debit.
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