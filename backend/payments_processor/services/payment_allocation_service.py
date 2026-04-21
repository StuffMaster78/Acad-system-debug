from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from payments_processor.constants import DEFAULT_CURRENCY
from payments_processor.enums import (
    PaymentAllocationStatus,
    PaymentAllocationType,
    PaymentIntentPurpose,
)
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentAllocation
from payments_processor.services.payment_intent_service import PaymentIntentService
from payments_processor.utils.references import generate_payment_reference
from wallets.services.wallet_hold_service import WalletHoldService
from wallets.models.wallet import Wallet
from wallets.services.client_wallet_service import ClientWalletService


class PaymentAllocationService:
    """
    Handles hybrid wallet plus external payment allocation.
    """

    @classmethod
    @transaction.atomic
    def create_allocations_for_payable(
        cls,
        *,
        client,
        payable,
        purpose: str,
        total_amount: Decimal,
        provider: str | None = None,
        currency: str = DEFAULT_CURRENCY,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create settlement allocations for a payable.

        Behavior:
        1. Use client wallet first if available
        2. If wallet fully covers, create wallet allocation only
        3. If wallet partially covers, create wallet allocation plus
           external payment intent for the remainder
        4. If wallet has no usable balance, create external payment only
        """
        if total_amount <= Decimal("0.00"):
            raise PaymentError("Total amount must be greater than zero.")

        metadata = metadata or {}

        wallet = ClientWalletService._get_client_wallet(client=client, currency=currency)
        wallet_available = ClientWalletService._get_wallet_available_balance(wallet=wallet)

        wallet_amount = min(wallet_available, total_amount)
        external_amount = total_amount - wallet_amount

        allocations: list[PaymentAllocation] = []
        payment_intent = None

        if wallet_amount > Decimal("0.00"):
            wallet_allocation = cls._create_wallet_allocation(
                client=client,
                payable=payable,
                wallet=wallet,
                amount=wallet_amount,
                currency=currency,
                reserve=(external_amount > Decimal("0.00")),
                metadata=metadata,
            )
            allocations.append(wallet_allocation)

        if external_amount > Decimal("0.00"):
            if not provider:
                raise PaymentError(
                    "Provider is required when external payment is needed."
                )

            intent_result = PaymentIntentService.create_intent(
                client=client,
                provider=provider,
                purpose=purpose,
                amount=external_amount,
                currency=currency,
                payable=payable,
                metadata=metadata,
                reference_prefix="pay",
            )
            payment_intent = intent_result["payment_intent"]

            external_allocation = cls._create_external_allocation(
                client=client,
                payable=payable,
                payment_intent=payment_intent,
                amount=external_amount,
                currency=currency,
                metadata=metadata,
            )
            allocations.append(external_allocation)

            return {
                "mode": "hybrid" if wallet_amount > Decimal("0.00") else "external_only",
                "total_amount": total_amount,
                "wallet_amount": wallet_amount,
                "external_amount": external_amount,
                "allocations": allocations,
                "payment_intent": payment_intent,
                "provider_data": intent_result["provider_data"],
            }

        return {
            "mode": "wallet_only",
            "total_amount": total_amount,
            "wallet_amount": wallet_amount,
            "external_amount": Decimal("0.00"),
            "allocations": allocations,
            "payment_intent": None,
            "provider_data": {},
        }


    @classmethod
    def _create_wallet_allocation(
        cls,
        *,
        client,
        payable,
        wallet: Wallet | None,
        amount: Decimal,
        currency: str,
        reserve: bool,
        metadata: dict[str, Any],
    ) -> PaymentAllocation:
        """
        Create wallet allocation backed by a WalletHold.
        """
        if wallet is None:
            raise PaymentError("Wallet allocation requires a wallet.")

        wallet_hold = WalletHoldService.create_hold(
            website=wallet.website,
            wallet=wallet,
            amount=amount,
            reference=generate_payment_reference(prefix="hold"),
            reason="payment_allocation",
        )

        status = (
            PaymentAllocationStatus.RESERVED
            if reserve
            else PaymentAllocationStatus.PENDING
        )

        return PaymentAllocation.objects.create(
            reference=generate_payment_reference(prefix="alloc"),
            website=wallet.website,
            client=client,
            payable_content_type=ContentType.objects.get_for_model(payable),
            payable_object_id=payable.pk,
            allocation_type=PaymentAllocationType.WALLET,
            status=status,
            currency=currency,
            amount=amount,
            wallet_hold=wallet_hold,
            metadata=metadata,
        )

    @classmethod
    def _create_external_allocation(
        cls,
        *,
        client,
        payable,
        payment_intent,
        amount: Decimal,
        currency: str,
        metadata: dict[str, Any],
    ) -> PaymentAllocation:
        """
        Create an external payment allocation linked to a payment intent.
        """
        return PaymentAllocation.objects.create(
            reference=generate_payment_reference(prefix="alloc"),
            website=payment_intent.website,
            client=client,
            payable_content_type=ContentType.objects.get_for_model(payable),
            payable_object_id=payable.pk,
            allocation_type=PaymentAllocationType.EXTERNAL_PAYMENT,
            status=PaymentAllocationStatus.PENDING,
            currency=currency,
            amount=amount,
            payment_intent=payment_intent,
            metadata=metadata,
        )