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


class WriterLedgerService:
    """
    Handles writer financial flows.

    Covers:
        - earnings
        - bonuses
        - tips
        - fines
        - adjustments
        - payouts
        - dispute recovery/restoration
    """

    DEFAULT_CURRENCY = "USD"

    # -------------------------
    # Utilities
    # -------------------------

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        if amount <= Decimal("0.00"):
            raise ValueError("Amount must be greater than zero.")

    @staticmethod
    def _validate_tip_split(
        *,
        total: Decimal,
        writer_share: Decimal,
        platform_share: Decimal,
    ) -> None:
        if writer_share <= Decimal("0.00"):
            raise ValueError("Writer share must be positive.")

        if platform_share < Decimal("0.00"):
            raise ValueError("Platform share cannot be negative.")

        if writer_share + platform_share != total:
            raise ValueError("Tip split mismatch.")

    @staticmethod
    def _merge_metadata(
        *,
        base: dict[str, Any] | None,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            **extra,
            **(base or {}),
        }

    # -------------------------
    # EARNING ACCRUAL
    # -------------------------

    @staticmethod
    @transaction.atomic
    def post_writer_earning_accrual(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        related_object_type: str,
        related_object_id: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Dr Expense
        Cr Writer Payable
        """
        WriterLedgerService._validate_amount(amount=amount)

        expense = AccountService.get_system_account(
            website=website,
            key="writer_compensation_expense",
        )
        payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )

        lines = [
            JournalLineInput(
                ledger_account=expense,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description="Writer earning accrued.",
            ),
            JournalLineInput(
                ledger_account=payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
                description="Writer payable increased.",
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_EARNING_ACCRUAL,
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description="Writer earning accrual recorded.",
            reference=reference or related_object_id,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model=related_object_type,
            source_object_id=related_object_id,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                    "writer_reference": writer_reference,
                },
            ),
        )

    # -------------------------
    # BONUS
    # -------------------------

    @staticmethod
    @transaction.atomic
    def post_writer_bonus(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        WriterLedgerService._validate_amount(amount=amount)

        expense = AccountService.get_system_account(
            website=website,
            key="writer_bonus_expense",
        )
        payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )

        lines = [
            JournalLineInput(
                ledger_account=expense,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
                description=reason,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_BONUS,
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=reference or writer_id,
            source_app=SourceApp.ADMIN,
            source_model="User",
            source_object_id=writer_id,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                },
            ),
        )

    # -------------------------
    # TIP CREDIT
    # -------------------------

    @staticmethod
    @transaction.atomic
    def post_writer_tip_credit(
        *,
        website,
        total_tip_amount: Decimal,
        writer_share: Decimal,
        platform_share: Decimal,
        writer_reference: str,
        writer_id: str,
        tip_reference: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        WriterLedgerService._validate_amount(amount=total_tip_amount)
        WriterLedgerService._validate_tip_split(
            total=total_tip_amount,
            writer_share=writer_share,
            platform_share=platform_share,
        )

        clearing = AccountService.get_system_account(
            website=website,
            key="tip_allocation_clearing",
        )
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_tip_payable",
        )
        platform_margin = AccountService.get_system_account(
            website=website,
            key="platform_tip_margin",
        )

        lines = [
            JournalLineInput(
                ledger_account=clearing,
                entry_side=EntrySide.DEBIT,
                amount=total_tip_amount,
                description="Tip clearing consumed.",
            ),
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.CREDIT,
                amount=writer_share,
                wallet_reference=writer_reference,
                description="Writer tip allocated.",
            ),
            JournalLineInput(
                ledger_account=platform_margin,
                entry_side=EntrySide.CREDIT,
                amount=platform_share,
                description="Platform tip margin.",
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_TIP_CREDIT,
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description="Writer tip allocation recorded.",
            reference=tip_reference,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model="Tip",
            source_object_id=tip_reference,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                    "writer_reference": writer_reference,
                },
            ),
        )

    # -------------------------
    # PAYOUT
    # -------------------------

    @staticmethod
    @transaction.atomic
    def post_writer_payout(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        payout_id: str,
        external_reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Dr Writer Payable
        Cr Platform Cash
        """
        WriterLedgerService._validate_amount(amount=amount)

        payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        cash = AccountService.get_system_account(
            website=website,
            key="platform_cash",
        )

        lines = [
            JournalLineInput(
                ledger_account=payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=writer_reference,
                description="Writer payable reduced.",
            ),
            JournalLineInput(
                ledger_account=cash,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description="Cash paid to writer.",
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_PAYOUT,
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description="Writer payout recorded.",
            reference=payout_id,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model="WriterPayment",
            source_object_id=payout_id,
            external_reference=external_reference,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                    "writer_reference": writer_reference,
                },
            ),
        )
    


    @staticmethod
    @transaction.atomic
    def post_writer_fine(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        fine_id: str,
        reason: str = "Writer fine recorded.",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        WriterLedgerService._validate_amount(amount=amount)

        payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        recovery = AccountService.get_system_account(
            website=website,
            key="fines_recovery",
        )

        lines = [
            JournalLineInput(
                ledger_account=payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=writer_reference,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=recovery,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_FINE,
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=fine_id,
            source_app=SourceApp.FINES,
            source_model="Fine",
            source_object_id=fine_id,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                    "writer_reference": writer_reference,
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_writer_earning_recovery(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        WriterLedgerService._validate_amount(amount=amount)

        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        writer_recovery = AccountService.get_system_account(
            website=website,
            key="writer_recovery",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=writer_reference,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=writer_recovery,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_EARNING_RECOVERY,
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=reference,
            source_app=SourceApp.DISPUTES,
            source_model="Dispute",
            source_object_id=reference,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                    "writer_reference": writer_reference,
                    "type": "recovery",
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_writer_earning_restoration(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        WriterLedgerService._validate_amount(amount=amount)

        writer_recovery = AccountService.get_system_account(
            website=website,
            key="writer_recovery",
        )
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_recovery,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
                description=reason,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_EARNING_RESTORATION,
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=reference,
            source_app=SourceApp.DISPUTES,
            source_model="Dispute",
            source_object_id=reference,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                    "writer_reference": writer_reference,
                    "type": "restoration",
                },
            ),
        )

    @staticmethod
    @transaction.atomic
    def post_writer_recovery_applied_to_payout(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        payout_id: str,
        reason: str = "Writer recovery applied to payout.",
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        WriterLedgerService._validate_amount(amount=amount)

        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        writer_recovery = AccountService.get_system_account(
            website=website,
            key="writer_recovery",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                wallet_reference=writer_reference,
                description=reason,
                related_object_type="WriterPayment",
                related_object_id=payout_id,
            ),
            JournalLineInput(
                ledger_account=writer_recovery,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
                description=reason,
                related_object_type="WriterPayment",
                related_object_id=payout_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=(
                LedgerEntryType.WRITER_RECOVERY_APPLIED_TO_PAYOUT
            ),
            lines=lines,
            currency=WriterLedgerService.DEFAULT_CURRENCY,
            description=reason,
            reference=reference or payout_id,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model="WriterPayment",
            source_object_id=payout_id,
            triggered_by=triggered_by,
            metadata=WriterLedgerService._merge_metadata(
                base=metadata,
                extra={
                    "writer_id": writer_id,
                    "writer_reference": writer_reference,
                    "payout_id": payout_id,
                },
            ),
        )