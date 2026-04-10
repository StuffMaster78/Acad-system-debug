from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from payments_processor.enums import (
    PaymentAllocationStatus,
    PaymentAllocationType,
    PaymentApplicationStatus,
)
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentAllocation, PaymentIntent
from payments_processor.selectors.payment_allocation_selectors import (
    get_allocations_for_payable,
    get_external_allocation_for_payable,
    get_wallet_allocation_for_payable,
    payable_is_fully_allocated,
)


class PaymentAllocationApplicationService:
    """
    Applies settlement allocations safely and determines whether
    a payable is now fully settled.
    """

    @classmethod
    @transaction.atomic
    def apply_successful_external_payment(
        cls,
        *,
        payment_intent: PaymentIntent,
        total_amount: Decimal,
    ) -> dict[str, Any]:
        """
        Apply an external payment allocation after provider success.

        If a reserved wallet allocation exists for the same payable,
        finalize it as part of the hybrid settlement flow.
        """
        if payment_intent.payable is None:
            raise PaymentError(
                f"Payment '{payment_intent.reference}' has no payable object."
            )

        payable = payment_intent.payable

        external_allocation = get_external_allocation_for_payable(payable=payable)
        if external_allocation is None:
            raise PaymentError(
                f"No external allocation found for payment "
                f"'{payment_intent.reference}'."
            )

        if external_allocation.payment_intent_id != payment_intent.pk:
            raise PaymentError(
                f"External allocation does not match payment "
                f"'{payment_intent.reference}'."
            )

        cls._apply_external_allocation(external_allocation=external_allocation)

        wallet_allocation = get_wallet_allocation_for_payable(payable=payable)
        if wallet_allocation is not None:
            cls._apply_wallet_allocation_if_needed(
                wallet_allocation=wallet_allocation
            )

        fully_settled = payable_is_fully_allocated(
            payable=payable,
            total_amount=total_amount,
        )

        if fully_settled:
            cls._mark_payment_intent_as_applied(payment_intent=payment_intent)

        return {
            "payment_intent_id": payment_intent.id,
            "reference": payment_intent.reference,
            "payable_id": payable.pk,
            "fully_settled": fully_settled,
        }

    @classmethod
    @transaction.atomic
    def apply_wallet_only_payment(
        cls,
        *,
        payable,
        total_amount: Decimal,
    ) -> dict[str, Any]:
        """
        Apply a wallet-only settlement flow.
        """
        wallet_allocation = get_wallet_allocation_for_payable(payable=payable)
        if wallet_allocation is None:
            raise PaymentError("No wallet allocation found for payable.")

        cls._apply_wallet_allocation_if_needed(
            wallet_allocation=wallet_allocation
        )

        fully_settled = payable_is_fully_allocated(
            payable=payable,
            total_amount=total_amount,
        )

        return {
            "payable_id": payable.pk,
            "fully_settled": fully_settled,
        }

    @staticmethod
    def _apply_external_allocation(
        *,
        external_allocation: PaymentAllocation,
    ) -> None:
        """
        Mark external allocation as applied.
        """
        if external_allocation.status == PaymentAllocationStatus.APPLIED:
            return

        if external_allocation.allocation_type != PaymentAllocationType.EXTERNAL_PAYMENT:
            raise PaymentError("Allocation is not an external payment allocation.")

        external_allocation.status = PaymentAllocationStatus.APPLIED
        external_allocation.applied_at = timezone.now()
        external_allocation.save(
            update_fields=[
                "status",
                "applied_at",
                "updated_at",
            ]
        )

    @staticmethod
    def _apply_wallet_allocation_if_needed(
        *,
        wallet_allocation: PaymentAllocation,
    ) -> None:
        """
        Finalize wallet allocation if it is still pending or reserved.
        """
        if wallet_allocation.status == PaymentAllocationStatus.APPLIED:
            return

        if wallet_allocation.allocation_type != PaymentAllocationType.WALLET:
            raise PaymentError("Allocation is not a wallet allocation.")

        if wallet_allocation.status not in {
            PaymentAllocationStatus.PENDING,
            PaymentAllocationStatus.RESERVED,
        }:
            raise PaymentError(
                f"Wallet allocation '{wallet_allocation.reference}' cannot be "
                f"applied from status '{wallet_allocation.status}'."
            )

        # TODO:
        # Call wallet domain service here to:
        # 1. finalize reservation into debit
        # or
        # 2. debit wallet directly for wallet-only flow

        wallet_allocation.status = PaymentAllocationStatus.APPLIED
        wallet_allocation.applied_at = timezone.now()
        wallet_allocation.save(
            update_fields=[
                "status",
                "applied_at",
                "updated_at",
            ]
        )

    @staticmethod
    def release_wallet_allocation(
        *,
        wallet_allocation: PaymentAllocation,
        reason: str = "",
    ) -> PaymentAllocation:
        """
        Release a reserved wallet allocation when external payment fails,
        expires, or is canceled.
        """
        if wallet_allocation.allocation_type != PaymentAllocationType.WALLET:
            raise PaymentError("Only wallet allocations can be released.")

        if wallet_allocation.status == PaymentAllocationStatus.APPLIED:
            raise PaymentError(
                "Cannot release a wallet allocation that is already applied."
            )

        if wallet_allocation.status == PaymentAllocationStatus.RELEASED:
            return wallet_allocation

        # TODO:
        # Call wallet domain service here to release reservation

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

    @staticmethod
    def _mark_payment_intent_as_applied(
        *,
        payment_intent: PaymentIntent,
    ) -> None:
        """
        Mark payment intent as internally applied after successful settlement.
        """
        if payment_intent.application_status == PaymentApplicationStatus.APPLIED:
            return

        payment_intent.application_status = PaymentApplicationStatus.APPLIED
        payment_intent.application_error = ""
        payment_intent.save(
            update_fields=[
                "application_status",
                "application_error",
                "updated_at",
            ]
        )