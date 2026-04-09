from __future__ import annotations

from decimal import Decimal
from typing import Any

from ledger.constants import EntrySide, LedgerEntryType, SourceApp
from ledger.services.account_service import AccountService
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)


class GatewayLedgerService:
    """
    Posts external gateway captures and refunds.
    """

    @staticmethod
    def post_external_payment_capture(
        *,
        website,
        amount: Decimal,
        payment_intent_reference: str,
        external_reference: str,
        related_object_type: str,
        related_object_id: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        gateway_clearing = AccountService.get_system_account(
            website=website,
            key="gateway_clearing",
        )
        platform_cash = AccountService.get_system_account(
            website=website,
            key="platform_cash",
        )

        lines = [
            JournalLineInput(
                ledger_account=gateway_clearing,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
            JournalLineInput(
                ledger_account=platform_cash,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE,
            lines=lines,
            description="External gateway payment captured.",
            source_app=SourceApp.PAYMENTS,
            source_model=related_object_type,
            source_object_id=related_object_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )

    @staticmethod
    def post_external_refund(
        *,
        website,
        amount: Decimal,
        refund_id: str,
        payment_intent_reference: str,
        external_reference: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        refund_reserve = AccountService.get_system_account(
            website=website,
            key="refund_reserve",
        )
        gateway_clearing = AccountService.get_system_account(
            website=website,
            key="gateway_clearing",
        )

        lines = [
            JournalLineInput(
                ledger_account=refund_reserve,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                payment_intent_reference=payment_intent_reference,
                related_object_type="Refund",
                related_object_id=refund_id,
            ),
            JournalLineInput(
                ledger_account=gateway_clearing,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                payment_intent_reference=payment_intent_reference,
                related_object_type="Refund",
                related_object_id=refund_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.REFUND_EXTERNAL,
            lines=lines,
            description="External refund recorded.",
            source_app=SourceApp.REFUNDS,
            source_model="Refund",
            source_object_id=refund_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )