from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from audit_logging.services.audit_log_service import AuditLogService
from wallets.constants import (
    WalletEntryDirection,
    WalletEntryStatus,
    WalletStatus,
    WalletType,
)
from wallets.exceptions import (
    CrossTenantWalletAccessError,
    InsufficientWalletBalanceError,
    WalletEntryError,
    WalletInactiveError,
)
from wallets.models import Wallet, WalletEntry


class WalletService:
    @staticmethod
    def validate_positive_amount(amount: Decimal) -> None:
        if amount <= Decimal("0.00"):
            raise WalletEntryError("Amount must be greater than zero.")

    @staticmethod
    def assert_wallet_belongs_to_website(*, wallet: Wallet, website: Any) -> None:
        if cast(Any,wallet).website_id != website.id:
            raise CrossTenantWalletAccessError(
                "Wallet does not belong to the provided website."
            )

    @staticmethod
    def assert_wallet_active(wallet: Wallet) -> None:
        if wallet.status != WalletStatus.ACTIVE:
            raise WalletInactiveError("Wallet is not active.")

    @staticmethod
    def get_wallet_queryset():
        return Wallet.objects.select_related("website", "owner_user")

    @staticmethod
    def get_wallet_for_update(*, wallet_id: int) -> Wallet:
        return (
            Wallet.objects.select_for_update()
            .select_related("website", "owner_user")
            .get(id=wallet_id)
        )

    @staticmethod
    def get_or_create_wallet(
        *,
        website: Any,
        owner_user: Any,
        wallet_type: str,
        currency: str = "USD",
    ) -> Wallet:
        wallet, _ = Wallet.objects.get_or_create(
            website=website,
            owner_user=owner_user,
            wallet_type=wallet_type,
            currency=currency,
            defaults={
                "status": WalletStatus.ACTIVE,
            },
        )
        return wallet

    @staticmethod
    @transaction.atomic
    def credit_wallet(
        *,
        wallet: Wallet,
        amount: Decimal,
        entry_type: str,
        website: Any,
        created_by: Any | None = None,
        description: str = "",
        reference: str = "",
        reference_type: str = "",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> WalletEntry:
        WalletService.validate_positive_amount(amount)

        locked_wallet = WalletService.get_wallet_for_update(
            wallet_id=cast(Any, wallet).id
        )
        WalletService.assert_wallet_belongs_to_website(
            wallet=locked_wallet,
            website=website,
        )
        WalletService.assert_wallet_active(locked_wallet)

        balance_before = locked_wallet.available_balance

        Wallet.objects.filter(id=cast(Any, locked_wallet).id).update(
            available_balance=F("available_balance") + amount,
            total_credited=F("total_credited") + amount,
            last_activity_at=timezone.now(),
            updated_at=timezone.now(),
        )
        locked_wallet.refresh_from_db()

        entry = WalletEntry.objects.create(
            website=website,
            wallet=locked_wallet,
            entry_type=entry_type,
            direction=WalletEntryDirection.CREDIT,
            status=WalletEntryStatus.POSTED,
            amount=amount,
            balance_before=balance_before,
            balance_after=locked_wallet.available_balance,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            metadata=metadata or {},
            created_by=created_by,
        )

        WalletService._log_audit(
            action="wallet.credit.posted",
            website=website,
            actor=created_by,
            wallet=locked_wallet,
            entry=entry,
        )
        return entry

    @staticmethod
    @transaction.atomic
    def debit_wallet(
        *,
        wallet: Wallet,
        amount: Decimal,
        entry_type: str,
        website: Any,
        created_by: Any | None = None,
        description: str = "",
        reference: str = "",
        reference_type: str = "",
        reference_id: str = "",
        metadata: dict[str, Any] | None = None,
        allow_negative: bool = False,
    ) -> WalletEntry:
        WalletService.validate_positive_amount(amount)

        locked_wallet = WalletService.get_wallet_for_update(
            wallet_id=cast(Any, wallet).id
        )
        WalletService.assert_wallet_belongs_to_website(
            wallet=locked_wallet,
            website=website,
        )
        WalletService.assert_wallet_active(locked_wallet)

        balance_before = locked_wallet.available_balance

        if not allow_negative and balance_before < amount:
            raise InsufficientWalletBalanceError(
                "Insufficient wallet balance for this debit."
            )

        Wallet.objects.filter(id=cast(Any, locked_wallet).id).update(
            available_balance=F("available_balance") - amount,
            total_debited=F("total_debited") + amount,
            last_activity_at=timezone.now(),
            updated_at=timezone.now(),
        )
        locked_wallet.refresh_from_db()

        entry = WalletEntry.objects.create(
            website=website,
            wallet=locked_wallet,
            entry_type=entry_type,
            direction=WalletEntryDirection.DEBIT,
            status=WalletEntryStatus.POSTED,
            amount=amount,
            balance_before=balance_before,
            balance_after=locked_wallet.available_balance,
            reference=reference,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            metadata=metadata or {},
            created_by=created_by,
        )

        WalletService._log_audit(
            action="wallet.debit.posted",
            website=website,
            actor=created_by,
            wallet=locked_wallet,
            entry=entry,
        )
        return entry

    @staticmethod
    def prepare_split_amounts(
        *,
        wallet: Wallet,
        total_amount: Decimal,
    ) -> dict[str, Decimal | bool]:
        WalletService.validate_positive_amount(total_amount)

        wallet_amount = min(wallet.available_balance, total_amount)
        gateway_amount = total_amount - wallet_amount

        return {
            "wallet_amount": wallet_amount,
            "gateway_amount": gateway_amount,
            "is_fully_covered": gateway_amount == Decimal("0.00"),
        }

    @staticmethod
    def get_wallet_by_owner_and_type(
        *,
        website: Any,
        owner_user: Any,
        wallet_type: str,
        currency: str = "USD",
    ) -> Wallet:
        return WalletService.get_wallet_queryset().get(
            website=website,
            owner_user=owner_user,
            wallet_type=wallet_type,
            currency=currency,
        )

    @staticmethod
    def get_client_wallet(
        *,
        website: Any,
        owner_user: Any,
        currency: str = "USD",
    ) -> Wallet:
        return WalletService.get_or_create_wallet(
            website=website,
            owner_user=owner_user,
            wallet_type=WalletType.CLIENT,
            currency=currency,
        )

    @staticmethod
    def get_writer_wallet(
        *,
        website: Any,
        owner_user: Any,
        currency: str = "USD",
    ) -> Wallet:
        return WalletService.get_or_create_wallet(
            website=website,
            owner_user=owner_user,
            wallet_type=WalletType.WRITER,
            currency=currency,
        )

    @staticmethod
    def _log_audit(
        *,
        action: str,
        website: Any,
        actor: Any | None,
        wallet: Wallet,
        entry: WalletEntry,
    ) -> None:
        try:
            cast(Any, AuditLogService).log_action(
                action=action,
                actor=actor,
                target=wallet,
                website=website,
                metadata={
                    "wallet_id": cast(Any, wallet).id,
                    "wallet_entry_id": cast(Any, entry).id,
                    "wallet_type": wallet.wallet_type,
                    "entry_type": entry.entry_type,
                    "direction": entry.direction,
                    "amount": str(entry.amount),
                    "balance_before": str(entry.balance_before),
                    "balance_after": str(entry.balance_after),
                    "reference": entry.reference,
                    "reference_type": entry.reference_type,
                    "reference_id": entry.reference_id,
                },
            )
        except Exception:
            pass