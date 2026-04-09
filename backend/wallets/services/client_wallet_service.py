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


class ClientWalletService:
    @staticmethod
    def get_wallet(
        *,
        website: Any,
        client: Any,
        currency: str = "KES",
    ) -> Wallet:
        return WalletService.get_client_wallet(
            website=website,
            owner_user=client,
            currency=currency,
        )

    @staticmethod
    @transaction.atomic
    def fund_wallet(
        *,
        website: Any,
        client: Any,
        amount: Decimal,
        created_by: Any | None = None,
        description: str = "Wallet funded",
        reference: str = "",
        reference_type: str = "",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        wallet = ClientWalletService.get_wallet(
            website=website,
            client=client,
        )

        journal_entry = WalletLedgerIntegrationService.post_wallet_funding(
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
            entry_type=WalletEntryType.FUNDING,
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
                event_key="wallet.client.funded",
                recipient=client,
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
    def refund_to_wallet(
        *,
        website: Any,
        client: Any,
        amount: Decimal,
        created_by: Any | None = None,
        description: str = "Refund credited to wallet",
        reference: str = "",
        reference_type: str = "",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        wallet = ClientWalletService.get_wallet(
            website=website,
            client=client,
        )

        journal_entry = WalletLedgerIntegrationService.post_wallet_refund(
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
            entry_type=WalletEntryType.ORDER_REFUND,
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
                event_key="wallet.client.refunded",
                recipient=client,
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
    def debit_for_order(
        *,
        website: Any,
        client: Any,
        amount: Decimal,
        created_by: Any | None = None,
        description: str = "Wallet payment applied to order",
        reference: str = "",
        reference_type: str = "order",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Wallet:
        wallet = ClientWalletService.get_wallet(
            website=website,
            client=client,
        )

        journal_entry = WalletLedgerIntegrationService.post_wallet_order_payment(
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
            entry_type=WalletEntryType.ORDER_PAYMENT,
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
                event_key="wallet.client.debited",
                recipient=client,
                website=website,
                context={
                    "amount": str(amount),
                    "currency": wallet.currency,
                    "wallet_id": cast(Any, wallet).id,
                    "reference": reference,
                    "journal_entry_id": journal_entry.id,
                },
                triggered_by=created_by,
            )
        except Exception:
            pass

        wallet.refresh_from_db()
        return wallet

    @staticmethod
    def prepare_split_payment(
        *,
        website: Any,
        client: Any,
        total_amount: Decimal,
        currency: str = "KES",
    ) -> dict[str, Decimal | bool]:
        wallet = ClientWalletService.get_wallet(
            website=website,
            client=client,
            currency=currency,
        )
        return WalletService.prepare_split_amounts(
            wallet=wallet,
            total_amount=total_amount,
        )

    @staticmethod
    def place_checkout_hold(
        *,
        website: Any,
        client: Any,
        amount: Decimal,
        reason: str,
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "order",
        reference_id: str = "",
        expires_at: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletHold:
        wallet = ClientWalletService.get_wallet(
            website=website,
            client=client,
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
    def capture_checkout_hold(
        *,
        hold: WalletHold,
        captured_by: Any | None = None,
    ) -> WalletHold:
        return WalletHoldService.capture_hold(
            hold=hold,
            captured_by=captured_by,
        )

    @staticmethod
    def release_checkout_hold(
        *,
        hold: WalletHold,
        released_by: Any | None = None,
    ) -> WalletHold:
        return WalletHoldService.release_hold(
            hold=hold,
            released_by=released_by,
        )

    @staticmethod
    @transaction.atomic
    def apply_split_payment(
        *,
        website: Any,
        client: Any,
        total_amount: Decimal,
        reason: str,
        created_by: Any | None = None,
        reference: str = "",
        reference_type: str = "order",
        reference_id: str = "",
        expires_at: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        split = ClientWalletService.prepare_split_payment(
            website=website,
            client=client,
            total_amount=total_amount,
        )

        wallet_amount = cast(Decimal, split["wallet_amount"])
        gateway_amount = cast(Decimal, split["gateway_amount"])
        is_fully_covered = cast(bool, split["is_fully_covered"])

        hold = None
        if wallet_amount > Decimal("0.00"):
            hold = ClientWalletService.place_checkout_hold(
                website=website,
                client=client,
                amount=wallet_amount,
                reason=reason,
                created_by=created_by,
                reference=reference,
                reference_type=reference_type,
                reference_id=reference_id,
                expires_at=expires_at,
                metadata=metadata,
            )

        return {
            "wallet_amount": wallet_amount,
            "gateway_amount": gateway_amount,
            "is_fully_covered": is_fully_covered,
            "wallet_hold": hold,
        }