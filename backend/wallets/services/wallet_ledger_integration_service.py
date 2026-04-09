from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from ledger.models.journal_entry import JournalEntry
from ledger.models.ledger_account import LedgerAccount
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)
from wallets.constants import WalletEntryType


class WalletLedgerIntegrationService:
    """
    Bridge between wallet business events and the ledger journal system.

    This service posts balanced journal entries for wallet-related flows and
    returns the created JournalEntry so wallet activity records can link back
    to accounting truth.
    """

    @staticmethod
    def _get_account(*, website: Any, code: str) -> LedgerAccount:
        return LedgerAccount.objects.get(
            website=website,
            code=code,
            is_active=True,
        )

    @staticmethod
    def _wallet_liability_account(*, website: Any, wallet_type: str) -> LedgerAccount:
        if wallet_type == "client":
            return WalletLedgerIntegrationService._get_account(
                website=website,
                code="CLIENT_WALLET_LIABILITY",
            )

        if wallet_type == "writer":
            return WalletLedgerIntegrationService._get_account(
                website=website,
                code="WRITER_WALLET_LIABILITY",
            )

        raise ValueError(f"Unsupported wallet type: {wallet_type}")

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
        return JournalPostingService.post_entry(
            website=website,
            entry_type=entry_type,
            lines=lines,
            currency=wallet.currency,
            description=description,
            reference=reference,
            source_app=source_app,
            source_model=source_model,
            source_object_id=source_object_id or str(wallet.pk),
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            triggered_by=triggered_by,
            metadata={
                "wallet_id": wallet.pk,
                "wallet_type": wallet.wallet_type,
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
        Example:
        Dr GATEWAY_CLEARING
        Cr CLIENT_WALLET_LIABILITY / WRITER_WALLET_LIABILITY
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        gateway_clearing = WalletLedgerIntegrationService._get_account(
            website=website,
            code="GATEWAY_CLEARING",
        )

        lines = [
            JournalLineInput(
                ledger_account=gateway_clearing,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                payment_intent_reference=payment_intent_reference,
                related_object_type="wallet",
                related_object_id=str(wallet.pk),
                metadata={"wallet_entry_type": WalletEntryType.FUNDING},
            ),
            JournalLineInput(
                ledger_account=wallet_liability,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                payment_intent_reference=payment_intent_reference,
                related_object_type="wallet",
                related_object_id=str(wallet.pk),
                metadata={"wallet_entry_type": WalletEntryType.FUNDING},
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
        Example:
        Dr CLIENT_WALLET_LIABILITY
        Cr ORDER_FUNDS_HELD
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        order_funds_held = WalletLedgerIntegrationService._get_account(
            website=website,
            code="ORDER_FUNDS_HELD",
        )

        lines = [
            JournalLineInput(
                ledger_account=wallet_liability,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="order",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ORDER_PAYMENT},
            ),
            JournalLineInput(
                ledger_account=order_funds_held,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="order",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ORDER_PAYMENT},
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
        Example:
        Dr REFUND_CLEARING
        Cr wallet liability
        """
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        refund_clearing = WalletLedgerIntegrationService._get_account(
            website=website,
            code="REFUND_CLEARING",
        )

        lines = [
            JournalLineInput(
                ledger_account=refund_clearing,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="refund",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ORDER_REFUND},
            ),
            JournalLineInput(
                ledger_account=wallet_liability,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="refund",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ORDER_REFUND},
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
        Example:
        Dr ORDER_FUNDS_HELD
        Cr WRITER_WALLET_LIABILITY
        """
        writer_wallet_liability = WalletLedgerIntegrationService._get_account(
            website=website,
            code="WRITER_WALLET_LIABILITY",
        )
        order_funds_held = WalletLedgerIntegrationService._get_account(
            website=website,
            code="ORDER_FUNDS_HELD",
        )

        lines = [
            JournalLineInput(
                ledger_account=order_funds_held,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="order",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.EARNING},
            ),
            JournalLineInput(
                ledger_account=writer_wallet_liability,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="order",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.EARNING},
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
        Example:
        Dr PLATFORM_ADJUSTMENTS
        Cr WRITER_WALLET_LIABILITY
        """
        writer_wallet_liability = WalletLedgerIntegrationService._get_account(
            website=website,
            code="WRITER_WALLET_LIABILITY",
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code="PLATFORM_ADJUSTMENTS",
        )

        lines = [
            JournalLineInput(
                ledger_account=platform_adjustments,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="writer_bonus",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.BONUS},
            ),
            JournalLineInput(
                ledger_account=writer_wallet_liability,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="writer_bonus",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.BONUS},
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
        Example:
        Dr WRITER_WALLET_LIABILITY
        Cr PLATFORM_ADJUSTMENTS
        """
        writer_wallet_liability = WalletLedgerIntegrationService._get_account(
            website=website,
            code="WRITER_WALLET_LIABILITY",
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code="PLATFORM_ADJUSTMENTS",
        )

        lines = [
            JournalLineInput(
                ledger_account=writer_wallet_liability,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="writer_penalty",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.PENALTY},
            ),
            JournalLineInput(
                ledger_account=platform_adjustments,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="writer_penalty",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.PENALTY},
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
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code="PLATFORM_ADJUSTMENTS",
        )

        lines = [
            JournalLineInput(
                ledger_account=platform_adjustments,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ADMIN_CREDIT},
            ),
            JournalLineInput(
                ledger_account=wallet_liability,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ADMIN_CREDIT},
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
            source_object_id=source_object_id or str(wallet.pk),
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
        wallet_liability = WalletLedgerIntegrationService._wallet_liability_account(
            website=website,
            wallet_type=wallet.wallet_type,
        )
        platform_adjustments = WalletLedgerIntegrationService._get_account(
            website=website,
            code="PLATFORM_ADJUSTMENTS",
        )

        lines = [
            JournalLineInput(
                ledger_account=wallet_liability,
                entry_side="debit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ADMIN_DEBIT},
            ),
            JournalLineInput(
                ledger_account=platform_adjustments,
                entry_side="credit",
                amount=amount,
                description=description,
                user=wallet.owner_user,
                wallet_reference=str(wallet.pk),
                related_object_type="admin_adjustment",
                related_object_id=source_object_id,
                metadata={"wallet_entry_type": WalletEntryType.ADMIN_DEBIT},
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
            source_object_id=source_object_id or str(wallet.pk),
            triggered_by=created_by,
            metadata=metadata,
            lines=lines,
        )