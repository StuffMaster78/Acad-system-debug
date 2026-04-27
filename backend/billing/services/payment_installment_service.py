from __future__ import annotations

from datetime import datetime
from typing import Sequence, TypedDict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.models.installment import PaymentInstallment
from billing.models.invoice import Invoice
from billing.constants import InvoiceStatus


class PaymentInstallmentScheduleItem(TypedDict):
    """
    Represent a single installment entry in a schedule payload.
    """

    sequence_number: int
    amount: Decimal
    due_at: datetime


class PaymentInstallmentService:
    """
    Own write operations and lifecycle transitions for invoice
    installments.

    Installments belong to invoices and represent scheduled payment
    parts of a formal billing document.

    This service does not collect money or create provider payment
    intents. It only manages installment records and installment
    state.
    """

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate that an installment amount is greater than zero.

        Args:
            amount:
                Amount to validate.

        Raises:
            ValidationError:
                Raised when amount is zero or negative.
        """
        if amount <= Decimal("0"):
            raise ValidationError(
                "Installment amount must be greater than zero."
            )
        

    @staticmethod
    def _validate_amount_paid(
        *,
        amount: Decimal,
        amount_paid: Decimal,
    ) -> None:
        """
        Validate amount_paid against the installment amount.

        Args:
            amount:
                Scheduled installment amount.
            amount_paid:
                Allocated amount.

        Raises:
            ValidationError:
                Raised when amount_paid is negative or exceeds amount.
        """
        if amount_paid < Decimal("0"):
            raise ValidationError(
                "Installment amount_paid cannot be negative."
            )

        if amount_paid > amount:
            raise ValidationError(
                "Installment amount_paid cannot exceed amount."
            )
        

    @staticmethod
    def _validate_schedule_payload(
        *,
        invoice: Invoice,
        schedule: Sequence[PaymentInstallmentScheduleItem],
    ) -> None:
        """
        Validate installment schedule input.

        Args:
            invoice:
                Invoice that will own the installments.
            schedule:
                Sequence of installment payload dictionaries.

        Raises:
            ValidationError:
                Raised when the schedule is empty or does not sum to the
                invoice amount.
        """
        if not schedule:
            raise ValidationError(
                "Installment schedule cannot be empty."
            )

        total = Decimal("0")
        seen_sequence_numbers: set[int] = set()

        for item in schedule:
            sequence_number = item["sequence_number"]
            amount = item["amount"]
            due_at = item["due_at"]

            if sequence_number in seen_sequence_numbers:
                raise ValidationError(
                    "Installment sequence numbers must be unique."
                )

            if due_at is None:
                raise ValidationError(
                    "Each installment must have a due_at value."
                )

            cls = PaymentInstallmentService
            cls._validate_amount(amount=amount)

            seen_sequence_numbers.add(sequence_number)
            total += amount

        if total != invoice.amount:
            raise ValidationError(
                "Installment schedule total must equal invoice amount."
            )

    @staticmethod
    def _get_locked_installment(
        *,
        installment_id: int,
    ) -> PaymentInstallment:
        """
        Retrieve and lock an installment for safe mutation.

        Args:
            installment_id:
                Installment primary key.

        Returns:
            PaymentInstallment:
                Locked installment instance.
        """
        return PaymentInstallment.objects.select_for_update().get(
            pk=installment_id
        )

    @classmethod
    @transaction.atomic
    def create_schedule(
        cls,
        *,
        invoice: Invoice,
        schedule: Sequence[PaymentInstallmentScheduleItem],
    ) -> list[PaymentInstallment]:
        """
        Create a full installment schedule for an invoice.

        Existing installments for the invoice are deleted before the new
        schedule is created. Use this only when the invoice is still in
        a mutable state.

        Args:
            invoice:
                Invoice that will own the installments.
            schedule:
                Sequence of dictionaries containing:
                    sequence_number
                    amount
                    due_at

        Returns:
            list[PaymentInstallment]:
                Created installment instances.

        Raises:
            ValidationError:
                Raised when the invoice is not mutable or the schedule is
                invalid.
        """
        if invoice.status in {
            InvoiceStatus.PAID, 
            InvoiceStatus.CANCELLED,
            InvoiceStatus.EXPIRED
        }:
            raise ValidationError(
                "Terminal invoices cannot receive installment schedules."
            )

        cls._validate_schedule_payload(
            invoice=invoice,
            schedule=schedule,
        )

        PaymentInstallment.objects.filter(invoice=invoice).delete()

        installments: list[PaymentInstallment] = []

        for item in sorted(schedule, key=lambda row: row["sequence_number"]):
            installment = PaymentInstallment.objects.create(
                website=invoice.website,
                invoice=invoice,
                sequence_number=item["sequence_number"],
                amount=item["amount"],
                amount_paid=Decimal("0.00"),
                due_at=item["due_at"],
            )
            installments.append(installment)

        return installments


    @classmethod
    @transaction.atomic
    def apply_allocation(
        cls,
        *,
        installment: PaymentInstallment,
        amount: Decimal,
        allocated_at=None,
    ) -> PaymentInstallment:
        """
        Apply an allocated payment amount to an installment.

        Args:
            installment:
                Installment to update.
            amount:
                Amount to allocate.
            allocated_at:
                Optional explicit timestamp used when the installment
                becomes fully paid.

        Returns:
            PaymentInstallment:
                Updated installment.

        Raises:
            ValidationError:
                Raised when the installment is cancelled, already fully
                paid, or the allocation amount is invalid.
        """
        if amount <= Decimal("0"):
            raise ValidationError(
                "Allocation amount must be greater than zero."
            )

        locked_installment = cls._get_locked_installment(
            installment_id=installment.pk
        )

        if locked_installment.cancelled_at is not None:
            raise ValidationError(
                "Cancelled installments cannot receive allocations."
            )

        if locked_installment.amount_paid >= locked_installment.amount:
            raise ValidationError(
                "Fully paid installments cannot receive allocations."
            )

        new_amount_paid = locked_installment.amount_paid + amount
        if new_amount_paid > locked_installment.amount:
            raise ValidationError(
                "Allocation would overpay the installment."
            )

        locked_installment.amount_paid = new_amount_paid

        if locked_installment.amount_paid >= locked_installment.amount:
            locked_installment.paid_at = allocated_at or timezone.now()

        cls._validate_amount_paid(
            amount=locked_installment.amount,
            amount_paid=locked_installment.amount_paid,
        )

        locked_installment.save(
            update_fields=["amount_paid", "paid_at", "updated_at"]
        )
        return locked_installment
    
    @classmethod
    @transaction.atomic
    def mark_paid(
        cls,
        *,
        installment: PaymentInstallment,
        paid_at=None,
    ) -> PaymentInstallment:
        """
        Mark an installment as fully paid.

        Args:
            installment:
                Installment to update.
            paid_at:
                Optional explicit paid timestamp.

        Returns:
            PaymentInstallment:
                Updated installment.

        Raises:
            ValidationError:
                Raised when installment is already terminal.
        """
        locked_installment = cls._get_locked_installment(
            installment_id=installment.pk
        )

        if locked_installment.cancelled_at is not None:
            raise ValidationError(
                "Cancelled installments cannot be marked paid."
            )

        locked_installment.paid_at = paid_at or timezone.now()
        locked_installment.save(
            update_fields=["paid_at", "updated_at"]
        )
        return locked_installment

    @classmethod
    @transaction.atomic
    def cancel_installment(
        cls,
        *,
        installment: PaymentInstallment,
        cancelled_at=None,
    ) -> PaymentInstallment:
        """
        Cancel an installment.

        Args:
            installment:
                Installment to update.
            cancelled_at:
                Optional explicit cancellation timestamp.

        Returns:
            PaymentInstallment:
                Updated installment.

        Raises:
            ValidationError:
                Raised when installment is already paid.
        """
        locked_installment = cls._get_locked_installment(
            installment_id=installment.pk
        )

        if locked_installment.paid_at is not None:
            raise ValidationError(
                "Paid installments cannot be cancelled."
            )

        locked_installment.cancelled_at = cancelled_at or timezone.now()
        locked_installment.save(
            update_fields=["cancelled_at", "updated_at"]
        )
        return locked_installment