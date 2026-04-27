from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction

from notifications_system.services.notification_service import NotificationService
from wallets.constants import WalletEntryType
from wallets.models import Wallet, WalletHold
from wallets.services.wallet_hold_service import WalletHoldService
from wallets.services.wallet_ledger_integration_service import (
    WalletLedgerIntegrationService,
)
from wallets.services.wallet_service import WalletService


class WriterWalletService:
    """
    Writer wallet orchestration service.

    Responsibilities:
        1. Resolve writer wallets for a tenant.
        2. Credit writer earnings and bonuses.
        3. Apply writer penalties and deductions.
        4. Reserve, release, and capture payout holds.
        5. Keep wallet entries linked to ledger journal entries.

    Important:
        This service must always receive website explicitly.
        Never infer tenant from writer.website.
    """

    @staticmethod
    def get_wallet(
        *,
        website: Any,
        writer: Any,
        currency: str = "USD",
    ) -> Wallet:
        """
        Return or create the writer wallet for the given tenant.
        """
        return WalletService.get_writer_wallet(
            website=website,
            owner_user=writer,
            currency=currency,
        )

    @staticmethod
    def _link_entry_to_journal(
        *,
        entry: Any,
        journal_entry: Any,
    ) -> None:
        """
        Link a wallet entry to the posted ledger journal entry.

        Pylance may not know dynamically added Django fields, so entry is Any.
        """
        entry.ledger_transaction = journal_entry
        entry.save(update_fields=["ledger_transaction", "updated_at"])

    @staticmethod
    def _notify_writer(
        *,
        event_key: str,
        writer: Any,
        website: Any,
        wallet: Wallet,
        amount: Decimal,
        journal_entry: Any,
        triggered_by: Any | None,
    ) -> None:
        """
        Best-effort writer wallet notification.

        Wallet mutations must not fail because notifications fail.
        """
        try:
            NotificationService.notify(
                event_key=event_key,
                recipient=writer,
                website=website,
                context={
                    "amount": str(amount),
                    "currency": wallet.currency,
                    "wallet_id": cast(Any, wallet).id,
                    "journal_entry_id": cast(Any, journal_entry).id,
                },
                triggered_by=triggered_by,
            )
        except Exception:
            pass

    @staticmethod
    @transaction.atomic
    def credit_earning(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        created_by: Any | None = None,
        description: str = "Writer earning credited",
        reference: str = "",
        reference_type: str = "order",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        """
        Credit a writer earning.

        Ledger:
            Dr ORDER_FUNDS_HELD
            Cr WRITER_WALLET_LIABILITY

        Wallet:
            Credit writer wallet.
        """
        wallet = WriterWalletService.get_wallet(
            website=website,
            writer=writer,
        )

        journal_entry = WalletLedgerIntegrationService.post_writer_earning(
            website=website,
            wallet=wallet,
            amount=amount,
            created_by=created_by,
            reference=reference,
            source_object_id=reference_id,
            description=description,
            metadata=metadata,
        )

        entry = WalletService.credit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=WalletEntryType.EARNING,
            website=website,
            created_by=created_by,
            description=description,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
        )

        WriterWalletService._link_entry_to_journal(
            entry=entry,
            journal_entry=journal_entry,
        )

        WriterWalletService._notify_writer(
            event_key="wallet.writer.earning_posted",
            writer=writer,
            website=website,
            wallet=wallet,
            amount=amount,
            journal_entry=journal_entry,
            triggered_by=created_by,
        )

        wallet.refresh_from_db()
        return wallet

    @staticmethod
    @transaction.atomic
    def apply_bonus(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        created_by: Any | None = None,
        description: str = "Writer bonus credited",
        reference: str = "",
        reference_type: str = "writer_bonus",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        """
        Credit a writer bonus.

        Ledger:
            Dr PLATFORM_ADJUSTMENTS
            Cr WRITER_WALLET_LIABILITY

        Wallet:
            Credit writer wallet.
        """
        wallet = WriterWalletService.get_wallet(
            website=website,
            writer=writer,
        )

        journal_entry = WalletLedgerIntegrationService.post_writer_bonus(
            website=website,
            wallet=wallet,
            amount=amount,
            created_by=created_by,
            reference=reference,
            source_object_id=reference_id,
            description=description,
            metadata=metadata,
        )

        entry = WalletService.credit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=WalletEntryType.BONUS,
            website=website,
            created_by=created_by,
            description=description,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
        )

        WriterWalletService._link_entry_to_journal(
            entry=entry,
            journal_entry=journal_entry,
        )

        WriterWalletService._notify_writer(
            event_key="wallet.writer.bonus_posted",
            writer=writer,
            website=website,
            wallet=wallet,
            amount=amount,
            journal_entry=journal_entry,
            triggered_by=created_by,
        )

        wallet.refresh_from_db()
        return wallet

    @staticmethod
    @transaction.atomic
    def apply_penalty(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        created_by: Any | None = None,
        description: str = "Writer penalty applied",
        reference: str = "",
        reference_type: str = "writer_penalty",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        """
        Apply a writer penalty.

        Ledger:
            Dr WRITER_WALLET_LIABILITY
            Cr PLATFORM_ADJUSTMENTS

        Wallet:
            Debit writer wallet.
        """
        wallet = WriterWalletService.get_wallet(
            website=website,
            writer=writer,
        )

        journal_entry = WalletLedgerIntegrationService.post_writer_penalty(
            website=website,
            wallet=wallet,
            amount=amount,
            created_by=created_by,
            reference=reference,
            source_object_id=reference_id,
            description=description,
            metadata=metadata,
        )

        entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=WalletEntryType.PENALTY,
            website=website,
            created_by=created_by,
            description=description,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
            allow_negative=False,
        )

        WriterWalletService._link_entry_to_journal(
            entry=entry,
            journal_entry=journal_entry,
        )

        WriterWalletService._notify_writer(
            event_key="wallet.writer.penalty_posted",
            writer=writer,
            website=website,
            wallet=wallet,
            amount=amount,
            journal_entry=journal_entry,
            triggered_by=created_by,
        )

        wallet.refresh_from_db()
        return wallet

    @staticmethod
    @transaction.atomic
    def reserve_for_payout(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str = "Payout reservation",
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "payout",
        reference_id: str = "",
        expires_at: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletHold:
        """
        Reserve writer wallet funds for payout.

        This moves money from available balance to pending balance.
        It does not yet mark the payout as externally settled.
        """
        wallet = WriterWalletService.get_wallet(
            website=website,
            writer=writer,
        )

        return WalletHoldService.create_hold(
            wallet=wallet,
            amount=amount,
            website=website,
            reason=reason,
            created_by=created_by,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            expires_at=expires_at,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def release_payout_reserve(
        *,
        hold: WalletHold,
        released_by: Any | None = None,
    ) -> WalletHold:
        """
        Release a payout reservation back to available balance.
        """
        return WalletHoldService.release_hold(
            hold=hold,
            released_by=released_by,
        )

    @staticmethod
    @transaction.atomic
    def mark_payout_settled(
        *,
        hold: WalletHold,
        settled_by: Any | None = None,
    ) -> WalletHold:
        """
        Capture a payout reservation after payout settlement.
        """
        return WalletHoldService.capture_hold(
            hold=hold,
            captured_by=settled_by,
        )

    # ------------------------------------------------------------------
    # Legacy compatibility wrappers
    # ------------------------------------------------------------------

    @staticmethod
    def credit_order_payment(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        created_by: Any | None = None,
        order_id: str = "",
        reference: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        """
        Legacy wrapper for crediting writer order earnings.
        """
        return WriterWalletService.credit_earning(
            website=website,
            writer=writer,
            amount=amount,
            created_by=created_by,
            description="Writer order payment credited",
            reference=reference or order_id,
            reference_type="order",
            reference_id=order_id,
            metadata=metadata,
        )

    @staticmethod
    def credit_order_payment_with_metadata(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        metadata: dict[str, Any],
        created_by: Any | None = None,
        order_id: str = "",
        reference: str = "",
    ) -> Wallet:
        """
        Legacy wrapper for order earnings with metadata.
        """
        return WriterWalletService.credit_order_payment(
            website=website,
            writer=writer,
            amount=amount,
            created_by=created_by,
            order_id=order_id,
            reference=reference,
            metadata=metadata,
        )

    @staticmethod
    def apply_fine(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "writer_fine",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        """
        Legacy wrapper for applying a writer fine.
        """
        return WriterWalletService.apply_penalty(
            website=website,
            writer=writer,
            amount=amount,
            created_by=created_by,
            description="Writer fine applied",
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
        )

    @staticmethod
    def apply_fine_with_metadata(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        metadata: dict[str, Any],
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "writer_fine",
        reference_id: str = "",
    ) -> Wallet:
        """
        Legacy wrapper for applying a writer fine with metadata.
        """
        return WriterWalletService.apply_fine(
            website=website,
            writer=writer,
            amount=amount,
            created_by=created_by,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
        )

    @staticmethod
    def deduct_amount(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        created_by: Any | None = None,
        description: str = "Writer wallet deduction",
        reference: str = "",
        reference_type: str = "writer_deduction",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        """
        Legacy wrapper for deducting from a writer wallet.
        """
        return WriterWalletService.apply_penalty(
            website=website,
            writer=writer,
            amount=amount,
            created_by=created_by,
            description=description,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def payout(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "payout",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
        auto_settle: bool = False,
    ) -> WalletHold:
        """
        Reserve writer funds for payout, optionally settling immediately.
        """
        hold = WriterWalletService.reserve_for_payout(
            website=website,
            writer=writer,
            amount=amount,
            reason="Writer payout reservation",
            created_by=created_by,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            metadata=metadata,
        )

        if auto_settle:
            WriterWalletService.mark_payout_settled(
                hold=hold,
                settled_by=created_by,
            )
            hold.refresh_from_db()

        return hold