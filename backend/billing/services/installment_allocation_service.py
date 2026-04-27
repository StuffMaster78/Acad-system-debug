from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.models.installment import PaymentInstallment
from billing.models.invoice import Invoice
from billing.selectors.payment_installment_selectors import (
    PaymentInstallmentSelector,
)
from billing.services.payment_installment_service import (
    PaymentInstallmentService,
)


@dataclass(frozen=True)
class InstallmentAllocationLine:
    """
    Represent a single allocation applied to an installment.
    """

    installment: PaymentInstallment
    amount_applied: Decimal


@dataclass(frozen=True)
class InstallmentAllocationResult:
    """
    Represent the outcome of allocating a payment across installments.
    """

    invoice: Invoice
    allocations: list[InstallmentAllocationLine]
    total_applied: Decimal
    remaining_unapplied: Decimal
    fully_allocated: bool


class InstallmentAllocationService:
    """
    Apply verified invoice payments across active installments in
    sequence order.

    Allocation rule:
        earliest unpaid active installment first
    """

    @classmethod
    @transaction.atomic
    def allocate_payment_to_invoice_installments(
        cls,
        *,
        invoice: Invoice,
        amount: Decimal,
    ) -> InstallmentAllocationResult:
        """
        Allocate a verified payment amount across an invoice's unpaid
        installments in sequence order.

        Args:
            invoice:
                Invoice whose installments should receive allocations.
            amount:
                Amount to allocate.

        Returns:
            InstallmentAllocationResult:
                Allocation summary.

        Raises:
            ValidationError:
                Raised when amount is invalid.
        """
        if amount <= Decimal("0"):
            raise ValidationError(
                "Allocation amount must be greater than zero."
            )

        installments = list(
            PaymentInstallmentSelector.get_unpaid_queryset_for_invoice(
                website=invoice.website,
                invoice=invoice,
            ).order_by("sequence_number", "due_at", "created_at")
        )

        allocations: list[InstallmentAllocationLine] = []
        remaining = amount
        allocated_at = timezone.now()

        for installment in installments:
            if remaining <= Decimal("0"):
                break

            balance = installment.amount - installment.amount_paid
            if balance <= Decimal("0"):
                continue

            amount_to_apply = min(balance, remaining)

            updated_installment = (
                PaymentInstallmentService.apply_allocation(
                    installment=installment,
                    amount=amount_to_apply,
                    allocated_at=allocated_at,
                )
            )

            allocations.append(
                InstallmentAllocationLine(
                    installment=updated_installment,
                    amount_applied=amount_to_apply,
                )
            )
            remaining -= amount_to_apply

        total_applied = amount - remaining

        return InstallmentAllocationResult(
            invoice=invoice,
            allocations=allocations,
            total_applied=total_applied,
            remaining_unapplied=remaining,
            fully_allocated=(remaining == Decimal("0")),
        )