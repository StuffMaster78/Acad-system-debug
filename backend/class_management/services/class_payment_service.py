from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction

from class_management.constants import (
    ClassPaymentSourceType,
    ClassTimelineEventType,
)
from class_management.exceptions import ClassPaymentError
from class_management.integration.class_wallet_payment_integration import (
    ClassWalletPaymentIntegration,
)
from class_management.models import (
    ClassInstallment,
    ClassInvoiceLink,
    ClassOrder,
    ClassPaymentAllocation,
)
from class_management.services.class_installment_service import (
    ClassInstallmentService,
)
from class_management.services.class_order_service import ClassOrderService
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)


@dataclass(frozen=True)
class ClassPaymentResult:
    """
    Result returned after preparing or applying a class payment.
    """

    class_order: ClassOrder
    amount_due: Decimal
    wallet_amount: Decimal
    external_amount: Decimal
    source_type: str
    checkout_url: str = ""
    payment_intent_id: str = ""
    allocation_id: int | None = None


class ClassPaymentService:
    """
    Coordinate class payments.

    This service does not own wallet, provider, billing, or ledger logic.
    It calls those apps and records the class-side allocation.
    """

    @classmethod
    @transaction.atomic
    def create_invoice_link(
        cls,
        *,
        class_order: ClassOrder,
        invoice_id: str,
        invoice_number: str = "",
        status: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ClassInvoiceLink:
        """
        Link a billing invoice to a class order.
        """
        return ClassInvoiceLink.objects.create(
            class_order=class_order,
            invoice_id=invoice_id,
            invoice_number=invoice_number,
            status=status,
            metadata=metadata or {},
        )

    @classmethod
    @transaction.atomic
    def prepare_payment(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
        payer,
        use_wallet: bool,
        installment: ClassInstallment | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ClassPaymentResult:
        """
        Prepare wallet, external, or split payment.

        If wallet covers the full amount, payment is applied immediately.
        If wallet partially covers the amount, wallet is deducted and an
        external checkout is created for the remaining amount.
        """
        cls._validate_payment_amount(
            class_order=class_order,
            amount=amount,
        )

        wallet_amount = Decimal("0.00")
        external_amount = amount
        wallet_transaction_id = ""

        if use_wallet:
            wallet_amount = cls._calculate_wallet_amount(
                class_order=class_order,
                payer=payer,
                amount=amount,
            )
            external_amount = amount - wallet_amount

        if wallet_amount > Decimal("0.00"):
            wallet_transaction_id = cls._debit_client_wallet(
                class_order=class_order,
                client=payer,
                amount=wallet_amount,
                metadata=metadata,
            )

        if external_amount <= Decimal("0.00"):
            return cls._apply_wallet_only_payment(
                class_order=class_order,
                amount=amount,
                payer=payer,
                installment=installment,
                wallet_amount=wallet_amount,
                wallet_transaction_id=wallet_transaction_id,
                metadata=metadata,
            )

        return cls._prepare_external_payment(
            class_order=class_order,
            amount=amount,
            payer=payer,
            installment=installment,
            wallet_amount=wallet_amount,
            external_amount=external_amount,
            wallet_transaction_id=wallet_transaction_id,
            metadata=metadata,
        )

    @classmethod
    @transaction.atomic
    def apply_successful_payment(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
        source_type: str,
        payer,
        installment: ClassInstallment | None = None,
        wallet_amount: Decimal = Decimal("0.00"),
        external_amount: Decimal = Decimal("0.00"),
        payment_intent_id: str = "",
        payment_transaction_id: str = "",
        wallet_transaction_id: str = "",
        ledger_entry_id: str = "",
        reference: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ClassPaymentAllocation:
        """
        Apply a successful payment to a class order.
        """
        cls._validate_payment_amount(
            class_order=class_order,
            amount=amount,
        )
        cls._ensure_payment_not_applied(
            payment_intent_id=payment_intent_id,
            payment_transaction_id=payment_transaction_id,
        )

        allocation = ClassPaymentAllocation.objects.create(
            class_order=class_order,
            source_type=source_type,
            amount=amount,
            wallet_amount=wallet_amount,
            external_amount=external_amount,
            installment=installment,
            payment_intent_id=payment_intent_id,
            payment_transaction_id=payment_transaction_id,
            wallet_transaction_id=wallet_transaction_id,
            ledger_entry_id=ledger_entry_id,
            reference=reference,
            metadata=metadata or {},
        )

        if installment is not None:
            ClassInstallmentService.apply_payment_to_installment(
                installment=installment,
                amount=amount,
                payment_intent_id=payment_intent_id,
                invoice_id=cls._get_metadata_value(
                    metadata=metadata,
                    key="invoice_id",
                ),
            )

        ClassOrderService.apply_payment(
            class_order=class_order,
            amount=amount,
            triggered_by=payer,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.PAYMENT_APPLIED,
            title="Class payment allocated",
            triggered_by=payer,
            metadata={
                "allocation_id": allocation.pk,
                "amount": str(amount),
                "source_type": source_type,
                "wallet_amount": str(wallet_amount),
                "external_amount": str(external_amount),
                "payment_intent_id": payment_intent_id,
            },
        )

        return allocation

    @classmethod
    @transaction.atomic
    def apply_external_payment_success(
        cls,
        *,
        class_order: ClassOrder,
        payer,
        amount: Decimal,
        payment_intent_id: str,
        payment_transaction_id: str,
        installment: ClassInstallment | None = None,
        wallet_amount: Decimal = Decimal("0.00"),
        wallet_transaction_id: str = "",
        ledger_entry_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ClassPaymentAllocation:
        """
        Apply a successful external or split payment callback.
        """
        source_type = (
            ClassPaymentSourceType.SPLIT
            if wallet_amount > Decimal("0.00")
            else ClassPaymentSourceType.EXTERNAL
        )
        total_amount = amount + wallet_amount

        return cls.apply_successful_payment(
            class_order=class_order,
            amount=total_amount,
            source_type=source_type,
            payer=payer,
            installment=installment,
            wallet_amount=wallet_amount,
            external_amount=amount,
            payment_intent_id=payment_intent_id,
            payment_transaction_id=payment_transaction_id,
            wallet_transaction_id=wallet_transaction_id,
            ledger_entry_id=ledger_entry_id,
            metadata=metadata,
        )

    @classmethod
    def _apply_wallet_only_payment(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
        payer,
        installment: ClassInstallment | None,
        wallet_amount: Decimal,
        wallet_transaction_id: str,
        metadata: dict[str, Any] | None,
    ) -> ClassPaymentResult:
        """
        Apply a payment fully covered by the client wallet.
        """
        allocation = cls.apply_successful_payment(
            class_order=class_order,
            amount=amount,
            source_type=ClassPaymentSourceType.WALLET,
            payer=payer,
            installment=installment,
            wallet_amount=wallet_amount,
            external_amount=Decimal("0.00"),
            wallet_transaction_id=wallet_transaction_id,
            metadata=metadata,
        )

        return ClassPaymentResult(
            class_order=allocation.class_order,
            amount_due=amount,
            wallet_amount=wallet_amount,
            external_amount=Decimal("0.00"),
            source_type=ClassPaymentSourceType.WALLET,
            allocation_id=allocation.pk,
        )

    @classmethod
    def _prepare_external_payment(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
        payer,
        installment: ClassInstallment | None,
        wallet_amount: Decimal,
        external_amount: Decimal,
        wallet_transaction_id: str,
        metadata: dict[str, Any] | None,
    ) -> ClassPaymentResult:
        """
        Create checkout for an external or split payment.
        """
        checkout = cls._create_external_checkout(
            class_order=class_order,
            payer=payer,
            amount=external_amount,
            installment=installment,
            metadata={
                **(metadata or {}),
                "wallet_amount": str(wallet_amount),
                "external_amount": str(external_amount),
                "wallet_transaction_id": wallet_transaction_id,
            },
        )

        payment_intent = checkout.get("payment_intent")
        provider_data = checkout.get("provider_data", {})

        source_type = (
            ClassPaymentSourceType.SPLIT
            if wallet_amount > Decimal("0.00")
            else ClassPaymentSourceType.EXTERNAL
        )

        return ClassPaymentResult(
            class_order=class_order,
            amount_due=amount,
            wallet_amount=wallet_amount,
            external_amount=external_amount,
            source_type=source_type,
            checkout_url=str(provider_data.get("checkout_url", "")),
            payment_intent_id=str(
                getattr(payment_intent, "reference", ""),
            ),
        )

    @classmethod
    def _calculate_wallet_amount(
        cls,
        *,
        class_order: ClassOrder,
        payer,
        amount: Decimal,
    ) -> Decimal:
        """
        Calculate how much of the payment can come from wallet.
        """
        available_balance = cls._get_client_wallet_balance(
            client=payer,
            website=class_order.website,
            currency=class_order.currency,
        )

        return min(available_balance, amount)

    @classmethod
    def _validate_payment_amount(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
    ) -> None:
        """
        Validate class payment amount.
        """
        if amount <= Decimal("0.00"):
            raise ClassPaymentError("Payment amount must be positive.")

        if class_order.final_amount <= Decimal("0.00"):
            raise ClassPaymentError(
                "Class order has no payable amount."
            )

        if class_order.balance_amount <= Decimal("0.00"):
            raise ClassPaymentError(
                "Class order is already fully paid."
            )

        if amount > class_order.balance_amount:
            raise ClassPaymentError(
                "Payment amount cannot exceed class balance."
            )

    @staticmethod
    def _ensure_payment_not_applied(
        *,
        payment_intent_id: str,
        payment_transaction_id: str,
    ) -> None:
        """
        Prevent double application of external payment callbacks.
        """
        if payment_intent_id:
            intent_exists = ClassPaymentAllocation.objects.filter(
                payment_intent_id=payment_intent_id,
            ).exists()

            if intent_exists:
                raise ClassPaymentError(
                    "This payment intent has already been applied."
                )

        if payment_transaction_id:
            transaction_exists = ClassPaymentAllocation.objects.filter(
                payment_transaction_id=payment_transaction_id,
            ).exists()

            if transaction_exists:
                raise ClassPaymentError(
                    "This payment transaction has already been applied."
                )

    @staticmethod
    def _get_client_wallet_balance(
        *,
        client,
        website,
        currency: str,
    ) -> Decimal:
        """
        Return client wallet available balance.
        """
        return ClassWalletPaymentIntegration.get_client_wallet_balance(
            client=client,
            website=website,
            currency=currency,
        )

    @staticmethod
    def _debit_client_wallet(
        *,
        class_order: ClassOrder,
        client,
        amount: Decimal,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Debit client wallet for class payment.
        """
        return ClassWalletPaymentIntegration.debit_client_wallet(
            client=client,
            website=class_order.website,
            amount=amount,
            currency=class_order.currency,
            reference=f"class_order:{class_order.pk}",
            created_by=client,
            metadata={
                **(metadata or {}),
                "class_order_id": str(class_order.pk),
            },
        )

    @staticmethod
    def _create_external_checkout(
        *,
        class_order: ClassOrder,
        payer,
        amount: Decimal,
        installment: ClassInstallment | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create an external payment checkout.
        """
        return ClassWalletPaymentIntegration.create_external_checkout(
            class_order=class_order,
            payer=payer,
            amount=amount,
            installment=installment,
            metadata=metadata,
        )

    @staticmethod
    def _get_metadata_value(
        *,
        metadata: dict[str, Any] | None,
        key: str,
    ) -> str:
        """
        Return a metadata value as a string.
        """
        if metadata is None:
            return ""

        value = metadata.get(key, "")
        return str(value)