from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.contrib.auth import get_user_model
from django.db import transaction

from notifications_system.services.notification_service import NotificationService
from wallets.constants import WalletEntryType
from wallets.models import Wallet, WalletHold
from wallets.services.wallet_hold_service import WalletHoldService
from wallets.services.wallet_ledger_integration_service import (
    WalletLedgerIntegrationService,
)
from wallets.services.wallet_service import WalletService

UserModel = get_user_model()


class WriterWalletService:
    @staticmethod
    def get_wallet(
        *,
        website: Any,
        writer: Any,
        currency: str = "USD",
    ) -> Wallet:
        return WalletService.get_writer_wallet(
            website=website,
            owner_user=writer,
            currency=currency,
        )

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
        cast(Any, entry).ledger_transaction = journal_entry
        entry.save(update_fields=["ledger_transaction", "updated_at"])

        try:
            NotificationService.notify(
                event_key="wallet.writer.earning_posted",
                recipient=writer,
                website=website,
                context={
                    "amount": str(amount),
                    "currency": wallet.currency,
                    "wallet_id": cast(Any, wallet).id,
                    "journal_entry_id": journal_entry.id,
                },
                triggered_by=created_by,
            )
        except Exception:
            pass

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
        reference_type: str = "",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
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
        cast(Any, entry).ledger_transaction = journal_entry
        entry.save(update_fields=["ledger_transaction", "updated_at"])

        try:
            NotificationService.notify(
                event_key="wallet.writer.bonus_posted",
                recipient=writer,
                website=website,
                context={
                    "amount": str(amount),
                    "currency": wallet.currency,
                    "wallet_id": cast(Any, wallet).id,
                    "journal_entry_id": journal_entry.id,
                },
                triggered_by=created_by,
            )
        except Exception:
            pass

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
        reference_type: str = "",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
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
        cast(Any, entry).ledger_transaction = journal_entry
        entry.save(update_fields=["ledger_transaction", "updated_at"])

        try:
            NotificationService.notify(
                event_key="wallet.writer.penalty_posted",
                recipient=writer,
                website=website,
                context={
                    "amount": str(amount),
                    "currency": wallet.currency,
                    "wallet_id": cast(Any, wallet).id,
                    "journal_entry_id": journal_entry.id,
                },
                triggered_by=created_by,
            )
        except Exception:
            pass

        wallet.refresh_from_db()
        return wallet

    @staticmethod
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
    def release_payout_reserve(
        *,
        hold: WalletHold,
        released_by: Any | None = None,
    ) -> WalletHold:
        return WalletHoldService.release_hold(
            hold=hold,
            released_by=released_by,
        )

    @staticmethod
    def mark_payout_settled(
        *,
        hold: WalletHold,
        settled_by: Any | None = None,
    ) -> WalletHold:
        return WalletHoldService.capture_hold(
            hold=hold,
            captured_by=settled_by,
        )