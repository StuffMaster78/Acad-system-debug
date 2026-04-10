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
from wallets.models import Wallet


class PaymentAllocationService:
    """
    Handles hybrid wallet plus external payment allocation.
    """

    @classmethod
    @transaction.atomic
    def create_allocations_for_payable(
        cls,
        *,
        customer,
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

        wallet = cls._get_client_wallet(customer=customer, currency=currency)
        wallet_available = cls._get_wallet_available_balance(wallet=wallet)

        wallet_amount = min(wallet_available, total_amount)
        external_amount = total_amount - wallet_amount

        allocations: list[PaymentAllocation] = []
        payment_intent = None

        if wallet_amount > Decimal("0.00"):
            wallet_allocation = cls._create_wallet_allocation(
                customer=customer,
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
                customer=customer,
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
                customer=customer,
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

    @staticmethod
    def _get_client_wallet(
        *,
        customer,
        currency: str,
    ) -> Wallet | None:
        """
        Return the customer's stored value wallet if it exists.
        """
        return (
            Wallet.objects.filter(
                owner=customer,
                wallet_type="client_stored_value",
                currency=currency,
                status="active",
            )
            .first()
        )

    @staticmethod
    def _get_wallet_available_balance(
        *,
        wallet: Wallet | None,
    ) -> Decimal:
        """
        Return available wallet balance or zero if wallet does not exist.
        """
        if wallet is None:
            return Decimal("0.00")

        return wallet.available_balance_cached

    @classmethod
    def _create_wallet_allocation(
        cls,
        *,
        customer,
        payable,
        wallet: Wallet | None,
        amount: Decimal,
        currency: str,
        reserve: bool,
        metadata: dict[str, Any],
    ) -> PaymentAllocation:
        """
        Create a wallet allocation, reserved if external payment is also needed.
        """
        if wallet is None:
            raise PaymentError("Wallet allocation requested without a wallet.")

        status = (
            PaymentAllocationStatus.RESERVED
            if reserve
            else PaymentAllocationStatus.PENDING
        )

        allocation = PaymentAllocation.objects.create(
            reference=generate_payment_reference(prefix="alloc"),
            customer=customer,
            payable_content_type=ContentType.objects.get_for_model(payable),
            payable_object_id=payable.pk,
            allocation_type=PaymentAllocationType.WALLET,
            status=status,
            currency=currency,
            amount=amount,
            wallet=wallet,
            metadata=metadata,
        )

        return allocation

    @classmethod
    def _create_external_allocation(
        cls,
        *,
        customer,
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
            customer=customer,
            payable_content_type=ContentType.objects.get_for_model(payable),
            payable_object_id=payable.pk,
            allocation_type=PaymentAllocationType.EXTERNAL_PAYMENT,
            status=PaymentAllocationStatus.PENDING,
            currency=currency,
            amount=amount,
            payment_intent=payment_intent,
            metadata=metadata,
        )