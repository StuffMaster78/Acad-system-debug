from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

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


VALID_WALLET_TYPES = {
    WalletType.CLIENT,
    WalletType.WRITER,
}


class WalletService:
    """
    Core wallet balance service.

    Rules:
        1. Tenant must always be explicit.
        2. Wallet must belong to the provided tenant.
        3. Amounts must be positive.
        4. Balance changes must be atomic.
        5. Wallet entries must record before and after balances.
    """

    @staticmethod
    def _validate_positive_amount(amount: Decimal) -> None:
        """
        Ensure wallet movement amount is positive.
        """
        if amount <= Decimal("0.00"):
            raise WalletEntryError("Amount must be greater than zero.")

    @staticmethod
    def _validate_wallet_type(wallet_type: str) -> None:
        """
        Ensure wallet type is one of the supported wallet types.
        """
        if wallet_type not in VALID_WALLET_TYPES:
            raise ValidationError("Invalid wallet type.")

    @staticmethod
    def assert_wallet_belongs_to_website(
        *,
        wallet: Wallet,
        website: Any,
    ) -> None:
        """
        Prevent cross-tenant wallet operations.
        """
        wallet_website_id = getattr(wallet, "website_id", None)
        website_id = getattr(website, "id", None)

        if wallet_website_id != website_id:
            raise CrossTenantWalletAccessError(
                "Wallet does not belong to the provided website."
            )

    @staticmethod
    def assert_wallet_active(wallet: Wallet) -> None:
        """
        Prevent balance changes on inactive wallets.
        """
        if wallet.status != WalletStatus.ACTIVE:
            raise WalletInactiveError("Wallet is not active.")

    @staticmethod
    def get_wallet_queryset():
        """
        Base wallet queryset with common relations selected.
        """
        return Wallet.objects.select_related("website", "owner_user")

    @staticmethod
    def get_wallet_for_update(*, wallet_id: int) -> Wallet:
        """
        Lock a wallet row for atomic balance updates.
        """
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
        """
        Return an existing wallet or create one for the tenant/user/type/currency.

        This method is tenant-safe because website is explicit and wallet_type
        is validated before lookup/creation.
        """
        WalletService._validate_wallet_type(wallet_type)

        wallet, _created = Wallet.objects.get_or_create(
            website=website,
            owner_user=owner_user,
            wallet_type=wallet_type,
            currency=currency,
            defaults={},
        )
        return wallet

    @classmethod
    @transaction.atomic
    def credit_wallet(
        cls,
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
        """
        Credit a wallet and create a posted wallet entry.

        This method locks the wallet row before updating the balance to avoid
        race conditions under concurrent requests.
        """
        cls._validate_positive_amount(amount)

        locked_wallet = cls.get_wallet_for_update(
            wallet_id=cast(Any, wallet).id,
        )
        cls.assert_wallet_belongs_to_website(
            wallet=locked_wallet,
            website=website,
        )
        cls.assert_wallet_active(locked_wallet)

        balance_before = locked_wallet.available_balance
        now = timezone.now()

        Wallet.objects.filter(id=cast(Any, locked_wallet).id).update(
            available_balance=F("available_balance") + amount,
            total_credited=F("total_credited") + amount,
            last_activity_at=now,
            updated_at=now,
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

        cls._log_audit(
            action="wallet.credit.posted",
            website=website,
            actor=created_by,
            wallet=locked_wallet,
            entry=entry,
        )
        return entry

    @classmethod
    @transaction.atomic
    def debit_wallet(
        cls,
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
        """
        Debit a wallet and create a posted wallet entry.

        Negative balances are rejected by default. Only pass allow_negative=True
        for explicitly approved operational flows.
        """
        cls._validate_positive_amount(amount)

        locked_wallet = cls.get_wallet_for_update(
            wallet_id=cast(Any, wallet).id,
        )
        cls.assert_wallet_belongs_to_website(
            wallet=locked_wallet,
            website=website,
        )
        cls.assert_wallet_active(locked_wallet)

        balance_before = locked_wallet.available_balance

        if not allow_negative and balance_before < amount:
            raise InsufficientWalletBalanceError(
                "Insufficient wallet balance for this debit."
            )

        now = timezone.now()

        Wallet.objects.filter(id=cast(Any, locked_wallet).id).update(
            available_balance=F("available_balance") - amount,
            total_debited=F("total_debited") + amount,
            last_activity_at=now,
            updated_at=now,
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

        cls._log_audit(
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
        """
        Calculate how much can be paid from wallet and gateway.

        This does not mutate balances.
        """
        WalletService._validate_positive_amount(total_amount)

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
        """
        Retrieve an existing tenant-scoped wallet by owner/type/currency.
        """
        WalletService._validate_wallet_type(wallet_type)

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
        """
        Return or create a client wallet for the resolved tenant.
        """
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
        """
        Return or create a writer wallet for the resolved tenant.
        """
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
        """
        Best-effort audit logging.

        Wallet operations must not fail because audit logging failed.
        """
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