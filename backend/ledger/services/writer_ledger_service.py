from __future__ import annotations

from decimal import Decimal
from typing import Any

from ledger.constants import EntrySide, LedgerEntryType, SourceApp
from ledger.services.account_service import AccountService
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)
# if not writer_reference:
#     raise ValueError("writer_reference is required")

class WriterLedgerService:
    """
    Handles writer financial flows:
    - earnings
    - bonuses
    - tips
    - fines
    - manual adjustments
    - payouts
    """

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

    @staticmethod
    def _validate_tip_split(
        total: Decimal,
        writer_share: Decimal,
        platform_share: Decimal,
    ) -> None:
        if writer_share <= 0:
            raise ValueError("Writer share must be positive")

        if platform_share < 0:
            raise ValueError("Platform share cannot be negative")

        if writer_share + platform_share != total:
            raise ValueError("Tip split does not match total amount")

    # -----------------------------
    # WRITER EARNING
    # -----------------------------
    @staticmethod
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
    ):
        WriterLedgerService._validate_amount(amount)

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
            ),
            JournalLineInput(
                ledger_account=payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_EARNING_ACCRUAL,
            lines=lines,
            description="Writer earning accrual recorded.",
            reference=reference,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model=related_object_type,
            source_object_id=related_object_id,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                **(metadata or {}),
            },
        )

    # -----------------------------
    # BONUS
    # -----------------------------
    @staticmethod
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
    ):
        WriterLedgerService._validate_amount(amount)

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
                description=reason,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_BONUS,
            lines=lines,
            description=reason,
            reference=reference,
            source_app=SourceApp.ADMIN,
            source_model="User",
            source_object_id=writer_id,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                **(metadata or {}),
            },
        )

    # -----------------------------
    # TIP ALLOCATION
    # -----------------------------
    @staticmethod
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
    ):
        WriterLedgerService._validate_amount(total_tip_amount)
        WriterLedgerService._validate_tip_split(
            total_tip_amount,
            writer_share,
            platform_share,
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
            ),
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.CREDIT,
                amount=writer_share,
            ),
            JournalLineInput(
                ledger_account=platform_margin,
                entry_side=EntrySide.CREDIT,
                amount=platform_share,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_TIP_CREDIT,
            lines=lines,
            description="Writer tip allocation recorded.",
            reference=tip_reference,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model="Tip",
            source_object_id=tip_reference,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                "total_tip_amount": str(total_tip_amount),
                "writer_share": str(writer_share),
                "platform_share": str(platform_share),
                **(metadata or {}),
            },
        )

    # -----------------------------
    # FINE
    # -----------------------------
    @staticmethod
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
    ):
        WriterLedgerService._validate_amount(amount)

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
                description=reason,
            ),
            JournalLineInput(
                ledger_account=recovery,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_FINE,
            lines=lines,
            description=reason,
            reference=fine_id,
            source_app=SourceApp.FINES,
            source_model="Fine",
            source_object_id=fine_id,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                **(metadata or {}),
            },
        )

    # -----------------------------
    # PAYOUT
    # -----------------------------
    @staticmethod
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
    ):
        WriterLedgerService._validate_amount(amount)

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
            ),
            JournalLineInput(
                ledger_account=cash,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_PAYOUT,
            lines=lines,
            description="Writer payout recorded.",
            reference=payout_id,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model="WriterPayment",
            source_object_id=payout_id,
            external_reference=external_reference,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                **(metadata or {}),
            },
        )
    

    @staticmethod
    def post_writer_manual_increase(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Record a manual increase to writer balance.

        This is used when support or admin increases writer payable due to
        bonuses, corrections, goodwill adjustments, or dispute reversals.
        """
        WriterLedgerService._validate_amount(amount)

        manual_adjustments = AccountService.get_system_account(
            website=website,
            key="manual_adjustments",
        )
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )

        lines = [
            JournalLineInput(
                ledger_account=manual_adjustments,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_MANUAL_INCREASE,
            lines=lines,
            description=reason,
            reference=reference,
            source_app=SourceApp.ADMIN,
            source_model="User",
            source_object_id=writer_id,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                "writer_reference": writer_reference,
                **(metadata or {}),
            },
        )

    
    @staticmethod
    def post_writer_manual_decrease(
        *,
        website,
        amount: Decimal,
        writer_reference: str,
        writer_id: str,
        reason: str,
        reference: str = "",
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Record a manual decrease to writer balance.

        This is used when support or admin reduces writer payable due to
        corrections, recoveries, cancellations, or other approved
        adjustments.
        """
        WriterLedgerService._validate_amount(amount)

        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        manual_adjustments = AccountService.get_system_account(
            website=website,
            key="manual_adjustments",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=manual_adjustments,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_MANUAL_DECREASE,
            lines=lines,
            description=reason,
            reference=reference,
            source_app=SourceApp.ADMIN,
            source_model="User",
            source_object_id=writer_id,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                "writer_reference": writer_reference,
                **(metadata or {}),
            },
        )

    @staticmethod
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
    ):
        """
        Record recovery of previously credited writer earnings.

        Used when:
        - client wins dispute
        - order is cancelled after payout
        """
        WriterLedgerService._validate_amount(amount)

        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )
        recovery_account = AccountService.get_system_account(
            website=website,
            key="writer_recovery",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=recovery_account,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_EARNING_RECOVERY,
            lines=lines,
            description=reason,
            reference=reference,
            source_app=SourceApp.DISPUTES,
            source_model="Dispute",
            source_object_id=reference,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                "writer_reference": writer_reference,
                "type": "recovery",
                **(metadata or {}),
            },
        )
    
    
    @staticmethod
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
    ):
        """
        Restore previously deducted writer earnings.

        Used when:
        - writer wins dispute after deduction
        """
        WriterLedgerService._validate_amount(amount)

        recovery_account = AccountService.get_system_account(
            website=website,
            key="writer_recovery",
        )
        writer_payable = AccountService.get_system_account(
            website=website,
            key="writer_payable",
        )

        lines = [
            JournalLineInput(
                ledger_account=recovery_account,
                entry_side=EntrySide.DEBIT,
                amount=amount,
                description=reason,
            ),
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=writer_reference,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_EARNING_RESTORATION,
            lines=lines,
            description=reason,
            reference=reference,
            source_app=SourceApp.DISPUTES,
            source_model="Dispute",
            source_object_id=reference,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                "writer_reference": writer_reference,
                "type": "restoration",
                **(metadata or {}),
            },
        )
    
    @staticmethod
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
    ):
        """
        Apply outstanding writer recovery against writer payable before cash
        payout is posted.
        """
        WriterLedgerService._validate_amount(amount)

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
                wallet_reference=writer_reference,
                related_object_type="WriterPayment",
                related_object_id=payout_id,
            ),
            JournalLineInput(
                ledger_account=writer_payable,
                entry_side=EntrySide.CREDIT,
                amount=amount,
                description=reason,
                wallet_reference=writer_reference,
                related_object_type="WriterPayment",
                related_object_id=payout_id,
            ),
        ]

        return JournalPostingService.post_entry(
            website=website,
            entry_type=LedgerEntryType.WRITER_RECOVERY_APPLIED_TO_PAYOUT,
            lines=lines,
            description=reason,
            reference=reference or payout_id,
            source_app=SourceApp.WRITER_PAYMENTS,
            source_model="WriterPayment",
            source_object_id=payout_id,
            triggered_by=triggered_by,
            metadata={
                "writer_id": writer_id,
                "writer_reference": writer_reference,
                **(metadata or {}),
            },
        )