from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from ledger.models.journal_entry import JournalEntry
from ledger.models.ledger_account import LedgerAccount
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)
from wallets.constants import WalletEntryType, WalletType


class WalletLedgerIntegrationService:
    """
    Bridge wallet business events to the double-entry ledger.

    Rules:
        1. The wallet must belong to the provided website.
        2. Amount must be positive.
        3. Every posting must be balanced.
        4. Wallet liability increases with credits and decreases with debits.
        5. This service posts accounting truth only. It does not mutate wallet
           balances directly.
    """

    ENTRY_SIDE_DEBIT = "debit"
    ENTRY_SIDE_CREDIT = "credit"

    ACCOUNT_CLIENT_WALLET_LIABILITY = "CLIENT_WALLET_LIABILITY"
    ACCOUNT_WRITER_WALLET_LIABILITY = "WRITER_WALLET_LIABILITY"
    ACCOUNT_GATEWAY_CLEARING = "GATEWAY_CLEARING"
    ACCOUNT_ORDER_FUNDS_HELD = "ORDER_FUNDS_HELD"
    ACCOUNT_REFUND_CLEARING = "REFUND_CLEARING"
    ACCOUNT_PLATFORM_ADJUSTMENTS = "PLATFORM_ADJUSTMENTS"

    @staticmethod
    def _wallet_pk(*, wallet: Any) -> str:
        """
        Return wallet primary key as a string.

        Django exposes pk dynamically, so cast keeps Pylance calm.
        """
        return str(cast(Any, wallet).pk)

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Ensure only positive money movements are posted.
        """
        if amount <= Decimal("0.00"):
            raise ValidationError("Ledger posting amount must be greater than zero.")

    @staticmethod
    def _validate_wallet_tenant(*, website: Any, wallet: Any) -> None:
        """
        Prevent posting ledger entries for a wallet from another tenant.
        """
        if getattr(wallet, "website_id", None) != getattr(website, "id", None):
            raise PermissionDenied("Cross-tenant wallet ledger posting denied.")

    @staticmethod
    def _get_account(*, website: Any, code: str) -> LedgerAccount:
        """
        Retrieve an active tenant-scoped ledger account.
        """
        return LedgerAccount.objects.get(
            website=website,
            code=code,
            is_active=True,
        )

    @staticmethod
    def _wallet_liability_account(
        *,
        website: Any,
        wallet_type: str,
    ) -> LedgerAccount:
        """
        Resolve wallet liability account by wallet type.
        """
        if wallet_type == WalletType.CLIENT:
            return WalletLedgerIntegrationService._get_account(
                website=website,
                code=WalletLedgerIntegrationService.ACCOUNT_CLIENT_WALLET_LIABILITY,
            )

        if wallet_type == WalletType.WRITER:
            return WalletLedgerIntegrationService._get_account(
                website=website,
                code=WalletLedgerIntegrationService.ACCOUNT_WRITER_WALLET_LIABILITY,
            )

        raise ValueError(f"Unsupported wallet type: {wallet_type}")

    @staticmethod
    def _line(
        *,
        ledger_account: LedgerAccount,
        entry_side: str,
        amount: Decimal,
        description: str,
        wallet: Any,
        wallet_entry_type: str,
        related_object_type: str,
        related_object_id: str = "",
        payment_intent_reference: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> JournalLineInput:
        """
        Build a journal line for a wallet-related posting.
        """
        wallet_pk = WalletLedgerIntegrationService._wallet_pk(wallet=wallet)

        return JournalLineInput(
            ledger_account=ledger_account,
            entry_side=entry_side,
            amount=amount,
            description=description,
            user=wallet.owner_user,
            wallet_reference=wallet_pk,
            payment_intent_reference=payment_intent_reference,
            related_object_type=related_object_type,
            related_object_id=related_object_id or wallet_pk,
            metadata={
                "wallet_entry_type": wallet_entry_type,
                "wallet_id": wallet_pk,
                "wallet_type": wallet.wallet_type,
                **(metadata or {}),
            },
        )

    @staticmethod
    def _post(
        *,
        website: Any,
        entry_type: str,
        wallet: Any,
        amount: Decimal,
        description: str,
        reference: str = "",
        source_app: str = "wallets",
        source_model: str = "Wallet",
        source_object_id: str = "",
        external_reference: str = "",
        payment_intent_reference: str = "",
        triggered_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
        lines: list[JournalLineInput],
    ) -> JournalEntry:
        """
        Post a tenant-safe wallet journal entry.
        """
        WalletLedgerIntegrationService._validate_wallet_tenant(
            website=website,
            wallet=wallet,
        )
        WalletLedgerIntegrationService._validate_amount(amount=amount)

        wallet_pk = WalletLedgerIntegrationService._wallet_pk(wallet=wallet)

        return JournalPostingService.post_entry(
            website=website,
            entry_type=entry_type,
            lines=lines,
            currency=wallet.currency,
            description=description,
            reference=reference,
            source_app=source_app,
            source_model=source_model,
            source_object_id=source_object_id or wallet_pk,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata={
                "wallet_id": wallet_pk,
                "wallet_type": wallet.wallet_type,
                "amount": str(amount),
                **(metadata or {}),
            },
        )

    @staticmethod
    @transaction.atomic
    def post_wallet_funding(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        external_reference: str = "",
        payment_intent_reference: str = "",
        description: str = "Wallet funding posted",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Post external wallet funding.

        Dr GATEWAY_CLEARING
        Cr CLIENT/WRITER_WALLET_LIABILITY
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        gateway_clearing = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_GATEWAY_CLEARING,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=gateway_clearing,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.FUNDING,
                related_object_type="wallet",
                payment_intent_reference=payment_intent_reference,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.FUNDING,
                related_object_type="wallet",
                payment_intent_reference=payment_intent_reference,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="wallet_topup",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_object_id=source_object_id,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )

    @staticmethod
    @transaction.atomic
    def post_wallet_order_payment(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        description: str = "Wallet payment applied to order",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Apply client wallet funds to an order.

        Dr CLIENT_WALLET_LIABILITY
        Cr ORDER_FUNDS_HELD
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        order_funds_held = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_ORDER_FUNDS_HELD,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ORDER_PAYMENT,
                related_object_type="order",
                related_object_id=source_object_id,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=order_funds_held,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ORDER_PAYMENT,
                related_object_type="order",
                related_object_id=source_object_id,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="wallet_order_payment",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_model="Order",
            source_object_id=source_object_id,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )

    @staticmethod
    @transaction.atomic
    def post_wallet_refund(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        description: str = "Refund credited to wallet",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Credit a refund to wallet.

        Dr REFUND_CLEARING
        Cr CLIENT/WRITER_WALLET_LIABILITY
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        refund_clearing = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_REFUND_CLEARING,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=refund_clearing,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ORDER_REFUND,
                related_object_type="refund",
                related_object_id=source_object_id,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ORDER_REFUND,
                related_object_type="refund",
                related_object_id=source_object_id,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="wallet_refund",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_model="Refund",
            source_object_id=source_object_id,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )

    @staticmethod
    @transaction.atomic
    def post_writer_earning(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        description: str = "Writer earning credited",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Credit writer earning from held order funds.

        Dr ORDER_FUNDS_HELD
        Cr WRITER_WALLET_LIABILITY
        """
        writer_wallet_liability = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_WRITER_WALLET_LIABILITY,
        )
        order_funds_held = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_ORDER_FUNDS_HELD,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=order_funds_held,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.EARNING,
                related_object_type="order",
                related_object_id=source_object_id,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=writer_wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.EARNING,
                related_object_type="order",
                related_object_id=source_object_id,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="writer_earning",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_model="Order",
            source_object_id=source_object_id,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )

    @staticmethod
    @transaction.atomic
    def post_writer_bonus(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        description: str = "Writer bonus credited",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Credit writer bonus.

        Dr PLATFORM_ADJUSTMENTS
        Cr WRITER_WALLET_LIABILITY
        """
        writer_wallet_liability = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_WRITER_WALLET_LIABILITY,
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_PLATFORM_ADJUSTMENTS,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=platform_adjustments,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.BONUS,
                related_object_type="writer_bonus",
                related_object_id=source_object_id,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=writer_wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.BONUS,
                related_object_type="writer_bonus",
                related_object_id=source_object_id,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="writer_bonus",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_model="WriterBonus",
            source_object_id=source_object_id,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )

    @staticmethod
    @transaction.atomic
    def post_writer_penalty(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        description: str = "Writer penalty applied",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Apply writer penalty.

        Dr WRITER_WALLET_LIABILITY
        Cr PLATFORM_ADJUSTMENTS
        """
        writer_wallet_liability = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_WRITER_WALLET_LIABILITY,
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_PLATFORM_ADJUSTMENTS,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=writer_wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.PENALTY,
                related_object_type="writer_penalty",
                related_object_id=source_object_id,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=platform_adjustments,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.PENALTY,
                related_object_type="writer_penalty",
                related_object_id=source_object_id,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="writer_penalty",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_model="WriterPenalty",
            source_object_id=source_object_id,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )

    @staticmethod
    @transaction.atomic
    def post_admin_credit(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        description: str = "Admin wallet credit",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Credit wallet manually.

        Dr PLATFORM_ADJUSTMENTS
        Cr CLIENT/WRITER_WALLET_LIABILITY
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_PLATFORM_ADJUSTMENTS,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=platform_adjustments,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ADMIN_CREDIT,
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ADMIN_CREDIT,
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="admin_wallet_credit",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_model="Wallet",
            source_object_id=source_object_id,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )

    @staticmethod
    @transaction.atomic
    def post_admin_debit(
        *,
        website: Any,
        wallet: Any,
        amount: Decimal,
        created_by: Any | None = None,
        reference: str = "",
        source_object_id: str = "",
        description: str = "Admin wallet debit",
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """
        Debit wallet manually.

        Dr CLIENT/WRITER_WALLET_LIABILITY
        Cr PLATFORM_ADJUSTMENTS
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code=WalletLedgerIntegrationService.ACCOUNT_PLATFORM_ADJUSTMENTS,
        )

        lines = [
            WalletLedgerIntegrationService._line(
                ledger_account=wallet_liability,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_DEBIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ADMIN_DEBIT,
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
            ),
            WalletLedgerIntegrationService._line(
                ledger_account=platform_adjustments,
                entry_side=WalletLedgerIntegrationService.ENTRY_SIDE_CREDIT,
                amount=amount,
                description=description,
                wallet=wallet,
                wallet_entry_type=WalletEntryType.ADMIN_DEBIT,
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
            ),
        ]

        return WalletLedgerIntegrationService._post(
            website=website,
            entry_type="admin_wallet_debit",
            wallet=wallet,
            amount=amount,
            description=description,
            reference=reference,
            source_model="Wallet",
            source_object_id=source_object_id,
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )