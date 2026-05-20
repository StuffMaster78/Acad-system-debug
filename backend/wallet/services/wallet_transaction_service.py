from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from notifications_system.services.notification_service import NotificationService
from wallet.exceptions import InsufficientWalletBalance
from wallets.constants import WalletEntryType, WalletType
from wallets.models import Wallet, WalletEntry
from wallets.services.wallet_service import WalletService


class WalletTransactionService:
    """
    Legacy compatibility facade over the canonical wallets app.

    New code should import from wallets.services directly. This class exists
    so older call sites can keep working while all balance mutations land in
    wallets.Wallet / wallets.WalletEntry.
    """

    LEGACY_TYPE_TO_ENTRY_TYPE = {
        "top-up": WalletEntryType.FUNDING,
        "refund": WalletEntryType.ORDER_REFUND,
        "bonus": WalletEntryType.BONUS,
        "referral_bonus": WalletEntryType.REFERRAL_BONUS,
        "loyalty_point": WalletEntryType.LOYALTY_CONVERSION,
        "loyalty_conversion": WalletEntryType.LOYALTY_CONVERSION,
        "credit": WalletEntryType.ADMIN_CREDIT,
        "debit": WalletEntryType.ADMIN_DEBIT,
        "adjustment": WalletEntryType.ADMIN_ADJUSTMENT,
        "payment": WalletEntryType.ORDER_PAYMENT,
        "order_payment": WalletEntryType.EARNING,
        "fine": WalletEntryType.FINE,
        "deduction": WalletEntryType.DEDUCTION,
        "withdrawal": WalletEntryType.PAYOUT_SETTLED,
        "payout": WalletEntryType.PAYOUT_SETTLED,
    }

    @staticmethod
    def get_wallet(user, website, currency: str = "USD") -> Wallet:
        wallet_type = WalletTransactionService._wallet_type_for_user(user)
        return WalletService.get_or_create_wallet(
            website=website,
            owner_user=user,
            wallet_type=wallet_type,
            currency=currency,
        )

    @staticmethod
    def get_balance(user, website, currency: str = "USD") -> Decimal:
        wallet = WalletTransactionService.get_wallet(
            user=user,
            website=website,
            currency=currency,
        )
        return Decimal(str(wallet.available_balance))

    @staticmethod
    @transaction.atomic
    def credit(
        user,
        amount,
        website,
        description="",
        source="",
        note="",
        reference=None,
        metadata=None,
        transaction_type: str = "credit",
        created_by: Any | None = None,
    ) -> WalletEntry:
        wallet = WalletTransactionService.get_wallet(user, website)
        amount = Decimal(str(amount))
        entry_type = WalletTransactionService._entry_type(transaction_type)

        entry = WalletService.credit_wallet(
            wallet=wallet,
            website=website,
            amount=amount,
            entry_type=entry_type,
            created_by=created_by,
            description=description or note,
            reference=str(reference or ""),
            reference_type=source or transaction_type,
            metadata=metadata or {},
        )

        WalletTransactionService._notify(
            event_key="wallet.credited",
            recipient=user,
            website=website,
            amount=amount,
        )
        return entry

    @staticmethod
    @transaction.atomic
    def debit(
        user,
        website,
        amount,
        description="",
        source="",
        note="",
        reference=None,
        metadata=None,
        transaction_type: str = "debit",
        created_by: Any | None = None,
    ) -> WalletEntry:
        wallet = WalletTransactionService.get_wallet(user, website)
        amount = Decimal(str(amount))
        if wallet.available_balance < amount:
            raise InsufficientWalletBalance(
                f"Insufficient funds. Current balance: {wallet.available_balance}"
            )

        entry = WalletService.debit_wallet(
            wallet=wallet,
            website=website,
            amount=amount,
            entry_type=WalletTransactionService._entry_type(transaction_type),
            created_by=created_by,
            description=description or note,
            reference=str(reference or ""),
            reference_type=source or transaction_type,
            metadata=metadata or {},
        )

        WalletTransactionService._notify(
            event_key="wallet.debited",
            recipient=user,
            website=website,
            amount=amount,
        )
        return entry

    @staticmethod
    def refund(
        user,
        website,
        amount,
        description="",
        source="",
        note="",
        reference=None,
        metadata=None,
        created_by: Any | None = None,
    ) -> WalletEntry:
        return WalletTransactionService.credit(
            user=user,
            website=website,
            amount=amount,
            description=description or "Wallet refund",
            source=source or "refund",
            note=note,
            reference=reference,
            metadata=metadata,
            transaction_type="refund",
            created_by=created_by,
        )

    @staticmethod
    def _wallet_type_for_user(user) -> str:
        role = getattr(user, "role", "") or ""
        if role == "writer":
            return WalletType.WRITER
        return WalletType.CLIENT

    @staticmethod
    def _entry_type(transaction_type: str) -> str:
        return WalletTransactionService.LEGACY_TYPE_TO_ENTRY_TYPE.get(
            transaction_type,
            WalletEntryType.ADMIN_ADJUSTMENT,
        )

    @staticmethod
    def _notify(*, event_key: str, recipient, website, amount: Decimal) -> None:
        try:
            NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=website,
                context={
                    "amount": amount,
                    "website": website,
                },
            )
        except Exception:
            pass
