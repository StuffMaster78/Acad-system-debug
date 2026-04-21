from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from ledger.services.payment_processor_ledger_service import (
    PaymentProcessorLedgerService,
)

from payments_processor.enums import (
    PaymentAllocationStatus,
    PaymentAllocationType,
    PaymentApplicationStatus,
)
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentAllocation, PaymentIntent
from payments_processor.selectors.payment_allocation_selectors import (
    get_external_allocation_for_payable,
    get_wallet_allocation_for_payable,
    payable_is_fully_allocated,
)

from wallets.services.wallet_hold_service import WalletHoldService
from wallets.services.client_wallet_service import ClientWalletService


class PaymentAllocationApplicationService:
    """
    Applies settlement allocations safely.

    This is where:
    - apply external allocation
    - wallet holds are captured
    - wallet balances are debited
    - allocations become real money movement
    - Capture or debit wallet allocation
    - update payment intent application state when fully settled.
    """

    # ------------------------------------------------------------------ #
    # EXTERNAL PAYMENT FLOW
    # ------------------------------------------------------------------ #

    @classmethod
    @transaction.atomic
    def apply_successful_external_payment(
        cls,
        *,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
    ) -> dict[str, Any]:
        """
        Apply a successful external payment success
        and any linked wallet leg.
        """
        if payment_intent.payable is None:
            raise PaymentError(
                f"Payment '{payment_intent.reference}' has no payable."
            )

        payable = payment_intent.payable

        external_allocation = get_external_allocation_for_payable(
            payable=payable,
        )
        if external_allocation is None:
            raise PaymentError(
                f"No external allocation found for payment "
                f"'{payment_intent.reference}'."
            )

        if external_allocation.payment_intent is None:
            raise PaymentError("External allocation missing intent.")

        if external_allocation.payment_intent.pk != payment_intent.pk:
            raise PaymentError(
                f"External allocation mismatch for payment "
                f"'{payment_intent.reference}'."
            )

        cls._apply_external_allocation(
            external_allocation=external_allocation,
        )

        wallet_allocation = get_wallet_allocation_for_payable(
            payable=payable,
        )

        if wallet_allocation is not None:
            cls._apply_wallet_allocation_if_needed(
                wallet_allocation=wallet_allocation,
            )

        fully_settled = payable_is_fully_allocated(
            payable=payable,
            total_amount=total_amount,
        )

        if fully_settled:
            cls._mark_payment_intent_as_applied(
                payment_intent=payment_intent,
            )

        return {
            "payment_intent_id": payment_intent.pk,
            "reference": payment_intent.reference,
            "payable_id": getattr(payable, "pk", None),
            "fully_settled": fully_settled,
        }

    # ------------------------------------------------------------------ #
    # WALLET ONLY FLOW
    # ------------------------------------------------------------------ #

    @classmethod
    @transaction.atomic
    def apply_wallet_only_payment(
        cls,
        *,
        payable: Any,
        total_amount: Decimal,
    ) -> dict[str, Any]:
        """
        Apply wallet-only payment.
        """
        wallet_allocation = get_wallet_allocation_for_payable(
            payable=payable,
        )
        if wallet_allocation is None:
            raise PaymentError(
                "No wallet allocation found for payable."
            )

        cls._apply_wallet_allocation_if_needed(
            wallet_allocation=wallet_allocation,
        )

        fully_settled = payable_is_fully_allocated(
            payable=payable,
            total_amount=total_amount,
        )

        return {
            "payable_id": getattr(payable, "pk", None),
            "fully_settled": fully_settled,
        }

    # ------------------------------------------------------------------ #
    # APPLY EXTERNAL
    # ------------------------------------------------------------------ #

    @staticmethod
    def _apply_external_allocation(
        *,
        external_allocation: PaymentAllocation,
    ) -> None:
        """
        Mark external allocation as applied and post external capture
        to ledger exactly once.
        """
        if external_allocation.status == PaymentAllocationStatus.APPLIED:
            return

        if (
            external_allocation.allocation_type
            != PaymentAllocationType.EXTERNAL_PAYMENT
        ):
            raise PaymentError(
                "Allocation is not an external allocation."
            )
        

        payment_intent = external_allocation.payment_intent
        if payment_intent is None:
            raise PaymentError(
                f"External allocation '{external_allocation.reference}' "
                f"has no payment intent."
            )

        related_external_object = (
            f"{external_allocation.payable_content_type.app_label}."
            f"{external_allocation.payable_content_type.model}"
        )

        PaymentProcessorLedgerService.post_external_payment_capture(
            website=external_allocation.website,
            amount=external_allocation.amount,
            payment_intent_reference=payment_intent.reference,
            external_reference=external_allocation.reference,
            related_object_type=related_external_object,
            related_object_id=str(external_allocation.payable_object_id),
            reference=external_allocation.reference,
        )
        external_allocation.status = PaymentAllocationStatus.APPLIED
        external_allocation.applied_at = timezone.now()
        external_allocation.save(
            update_fields=[
                "status",
                "applied_at",
                "updated_at",
            ]
        )

    # ------------------------------------------------------------------ #
    # APPLY WALLET
    # ------------------------------------------------------------------ #

    @staticmethod
    def _apply_wallet_allocation_if_needed(
        *,
        wallet_allocation: PaymentAllocation,
    ) -> None:
        """
        Apply wallet allocation using wallet services.
        """
        if wallet_allocation.status == PaymentAllocationStatus.APPLIED:
            return

        if (
            wallet_allocation.allocation_type
            != PaymentAllocationType.WALLET
        ):
            raise PaymentError(
                "Allocation is not a wallet allocation."
            )

        wallet_hold = wallet_allocation.wallet_hold
        if wallet_hold is None:
            raise PaymentError(
                f"Wallet allocation '{wallet_allocation.reference}' "
                f"has no wallet hold."
            )

        if wallet_allocation.status == PaymentAllocationStatus.RESERVED:
            WalletHoldService.capture_hold(
                hold=wallet_hold,
            )

        elif wallet_allocation.status == PaymentAllocationStatus.PENDING:
            ClientWalletService.debit_for_order(
                website=wallet_hold.website,
                client=wallet_hold.wallet,
                amount=wallet_allocation.amount,
                reference=wallet_allocation.reference,
                reference_type="payment allocation",
                reference_id=str(wallet_allocation.pk),
                metadata={
                    "payment_allocation_id": wallet_allocation.pk,
                },
            )

        else:
            raise PaymentError(
                f"Cannot apply wallet allocation from status "
                f"'{wallet_allocation.status}'."
            )

        wallet_allocation.status = PaymentAllocationStatus.APPLIED
        wallet_allocation.applied_at = timezone.now()
        wallet_allocation.save(
            update_fields=[
                "status",
                "applied_at",
                "updated_at",
            ]
        )

    # ------------------------------------------------------------------ #
    # RELEASE WALLET
    # ------------------------------------------------------------------ #

    @staticmethod
    def release_wallet_allocation(
        *,
        wallet_allocation: PaymentAllocation,
        reason: str = "",
    ) -> PaymentAllocation:
        """
        Release wallet hold safely.
        """
        if (
            wallet_allocation.allocation_type
            != PaymentAllocationType.WALLET
        ):
            raise PaymentError(
                "Only wallet allocations can be released."
            )

        if wallet_allocation.status == PaymentAllocationStatus.APPLIED:
            raise PaymentError(
                "Cannot release already applied allocation."
            )

        if wallet_allocation.status == PaymentAllocationStatus.RELEASED:
            return wallet_allocation

        wallet_hold = wallet_allocation.wallet_hold
        if wallet_hold is None:
            raise PaymentError(
                "Wallet allocation has no wallet hold."
            )

        WalletHoldService.release_hold(
            hold=wallet_hold,
        )

        wallet_allocation.status = PaymentAllocationStatus.RELEASED
        wallet_allocation.released_at = timezone.now()
        wallet_allocation.failure_reason = reason
        wallet_allocation.save(
            update_fields=[
                "status",
                "released_at",
                "failure_reason",
                "updated_at",
            ]
        )

        return wallet_allocation

    # ------------------------------------------------------------------ #
    # MARK PAYMENT INTENT
    # ------------------------------------------------------------------ #

    @staticmethod
    def _mark_payment_intent_as_applied(
        *,
        payment_intent: PaymentIntent,
    ) -> None:
        """
        Mark payment intent as applied.
        """
        if (
            payment_intent.application_status
            == PaymentApplicationStatus.APPLIED
        ):
            return

        payment_intent.application_status = (
            PaymentApplicationStatus.APPLIED
        )
        payment_intent.application_error = ""
        payment_intent.save(
            update_fields=[
                "application_status",
                "application_error",
                "updated_at",
            ]
        )