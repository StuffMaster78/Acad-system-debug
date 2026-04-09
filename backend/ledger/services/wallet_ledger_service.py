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
    Posts wallet related financial entries.
    """

    @staticmethod
    def post_wallet_top_up(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        payment_intent_reference: str = "",
        external_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        gateway_clearing = AccountService.get_system_account(
            website=website,
            key="gateway_clearing",
        )
        client_wallet_liability = AccountService.get_system_account(
            website=website,
            key="client_wallet_liability",
        )

        lines = [
            JournalLineInput(
                ledger_account=gateway_clearing,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
            ),
            JournalLineInput(
                ledger_account=client_wallet_liability,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            lines=lines,
            description="Wallet top up recorded.",
            source_app=SourceApp.WALLETS,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )

    @staticmethod
    def post_wallet_debit_for_order(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        order_id: str,
        payment_intent_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        client_wallet_liability = AccountService.get_system_account(
            website=website,
            key="client_wallet_liability",
        )
        platform_cash = AccountService.get_system_account(
            website=website,
            key="platform_cash",
        )

        lines = [
            JournalLineInput(
                ledger_account=client_wallet_liability,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                related_object_type="Order",
                related_object_id=order_id,
            ),
            JournalLineInput(
                ledger_account=platform_cash,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                related_object_type="Order",
                related_object_id=order_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WALLET_DEBIT,
            lines=lines,
            description="Wallet debit for order payment.",
            source_app=SourceApp.ORDERS,
            source_model="Order",
            source_object_id=order_id,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )

    @staticmethod
    def post_wallet_refund(
        *,
        website,
        amount: Decimal,
        wallet_reference: str,
        refund_id: str,
        payment_intent_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        refund_reserve = AccountService.get_system_account(
            website=website,
            key="refund_reserve",
        )
        client_wallet_liability = AccountService.get_system_account(
            website=website,
            key="client_wallet_liability",
        )

        lines = [
            JournalLineInput(
                ledger_account=refund_reserve,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                related_object_type="Refund",
                related_object_id=refund_id,
            ),
            JournalLineInput(
                ledger_account=client_wallet_liability,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=wallet_reference,
                payment_intent_reference=payment_intent_reference,
                related_object_type="Refund",
                related_object_id=refund_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.REFUND_TO_WALLET,
            lines=lines,
            description="Refund credited back to wallet.",
            source_app=SourceApp.REFUNDS,
            source_model="Refund",
            source_object_id=refund_id,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )