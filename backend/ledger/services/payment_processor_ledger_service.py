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


class PaymentProcessorLedgerService:
    """
    Handle external processor money movement only.

    This service records payment processor movements in the ledger.
    It should not decide order status, wallet balances, writer earnings,
    refunds policy, or billing behavior.
    """

    DEFAULT_CURRENCY = "USD"

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate that an amount is positive.
        """
        if amount <= Decimal("0.00"):
            raise ValueError("Amount must be greater than zero.")

    @staticmethod
    def _build_metadata(
        *,
        base_metadata: dict[str, Any] | None,
        extra_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Merge service metadata safely.
        """
        return {
            **extra_metadata,
            **(base_metadata or {}),
        }

    @staticmethod
    @transaction.atomic
    def post_external_payment_capture(
        *,
        website,
        amount: Decimal,
        payment_intent_reference: str,
        external_reference: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Record a confirmed external payment capture.

        Accounting shape:
            Dr Platform Cash
            Cr Gateway Clearing
        """
        PaymentProcessorLedgerService._validate_amount(
            amount=amount,
        )

        platform_cash = AccountService.get_system_account(
            website=website,
            key="platform_cash",
        )
        gateway_clearing = AccountService.get_system_account(
            website=website,
            key="gateway_clearing",
        )

        entry_reference = reference or payment_intent_reference

        lines = [
            JournalLineInput(
                ledger_account=platform_cash,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description="External payment captured into platform cash.",
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
                metadata={
                    "external_reference": external_reference,
                },
            ),
            JournalLineInput(
                ledger_account=gateway_clearing,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description="Gateway clearing reduced after capture.",
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
                metadata={
                    "external_reference": external_reference,
                },
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE,
            lines=lines,
            currency=PaymentProcessorLedgerService.DEFAULT_CURRENCY,
            description="External payment capture recorded.",
            reference=entry_reference,
            source_app=SourceApp.PAYMENT_PROCESSOR,
            source_model=related_object_type,
            source_object_id=related_object_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=PaymentProcessorLedgerService._build_metadata(
                base_metadata=metadata,
                extra_metadata={
                    "payment_intent_reference": (
                        payment_intent_reference
                    ),
                    "external_reference": external_reference,
                    "related_object_type": related_object_type,
                    "related_object_id": related_object_id,
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_external_refund(
        *,
        website,
        amount: Decimal,
        refund_id: str,
        payment_intent_reference: str,
        external_reference: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Record a confirmed external refund.

        Accounting shape:
            Dr Gateway Clearing
            Cr Platform Cash
        """
        PaymentProcessorLedgerService._validate_amount(
            amount=amount,
        )

        gateway_clearing = AccountService.get_system_account(
            website=website,
            key="gateway_clearing",
        )
        platform_cash = AccountService.get_system_account(
            website=website,
            key="platform_cash",
        )

        entry_reference = reference or refund_id

        lines = [
            JournalLineInput(
                ledger_account=gateway_clearing,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description="Gateway clearing increased by external refund.",
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
                metadata={
                    "refund_id": refund_id,
                    "external_reference": external_reference,
                },
            ),
            JournalLineInput(
                ledger_account=platform_cash,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description="Platform cash reduced by external refund.",
                payment_intent_reference=payment_intent_reference,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
                metadata={
                    "refund_id": refund_id,
                    "external_reference": external_reference,
                },
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.EXTERNAL_REFUND,
            lines=lines,
            currency=PaymentProcessorLedgerService.DEFAULT_CURRENCY,
            description="External refund recorded.",
            reference=entry_reference,
            source_app=SourceApp.PAYMENT_PROCESSOR,
            source_model=related_object_type,
            source_object_id=related_object_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata=PaymentProcessorLedgerService._build_metadata(
                base_metadata=metadata,
                extra_metadata={
                    "refund_id": refund_id,
                    "payment_intent_reference": (
                        payment_intent_reference
                    ),
                    "external_reference": external_reference,
                    "related_object_type": related_object_type,
                    "related_object_id": related_object_id,
                },
            ),
        )