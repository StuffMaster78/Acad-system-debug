from __future__ import annotations

from decimal import Decimal
from typing import Any
from typing import cast

from wallets.constants import WalletEntryType


class ClassWalletPaymentIntegration:
    """
    Bridge class payments to wallets and payments_processor.
    """

    @staticmethod
    def get_client_wallet_balance(
        *,
        client,
        website,
        currency: str,
    ) -> Decimal:
        """
        Return the client's available wallet balance.
        """
        from wallets.services.wallet_service import WalletService

        wallet = WalletService.get_client_wallet(
            website=website,
            owner_user=client,
            currency=currency,
        )

        return wallet.available_balance

    @staticmethod
    def debit_client_wallet(
        *,
        client,
        website,
        amount: Decimal,
        currency: str,
        reference: str,
        metadata: dict[str, Any] | None = None,
        created_by=None,
    ) -> str:
        """
        Debit the client wallet for a class order payment.
        """
        from wallets.services.wallet_service import WalletService

        wallet = WalletService.get_client_wallet(
            website=website,
            owner_user=client,
            currency=currency,
        )

        entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=WalletEntryType.ORDER_PAYMENT,
            website=website,
            created_by=created_by or client,
            description="Class order wallet payment",
            reference=reference,
            reference_type="class_order",
            reference_id=ClassWalletPaymentIntegration._metadata_value(
                metadata=metadata,
                key="class_order_id",
            ),
            metadata=metadata or {},
        )

        return str(cast(Any, entry).pk)

    @staticmethod
    def create_external_checkout(
        *,
        class_order,
        payer,
        amount: Decimal,
        installment=None,
        metadata: dict[str, Any] | None = None,
        provider: str = "stripe",
    ) -> dict[str, Any]:
        """
        Create an external checkout through payments_processor.
        """
        from payments_processor.services.payment_intent_service import (
            PaymentIntentService,
        )

        return PaymentIntentService.create_intent(
            client=payer,
            provider=provider,
            purpose="class_order_payment",
            amount=amount,
            currency=class_order.currency,
            payable=class_order,
            metadata={
                **(metadata or {}),
                "class_order_id": str(class_order.pk),
                "installment_id": str(installment.pk)
                if installment is not None
                else "",
            },
            reference_prefix="class",
        )

    @staticmethod
    def _metadata_value(
        *,
        metadata: dict[str, Any] | None,
        key: str,
    ) -> str:
        """
        Return a metadata value as a string.
        """
        if metadata is None:
            return ""

        return str(metadata.get(key, ""))