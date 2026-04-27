from __future__ import annotations

from decimal import Decimal

from django.db.models import QuerySet
from django.utils import timezone

from billing.models.installment import PaymentInstallment


class PaymentInstallmentSelector:
    """
    Provide read-side helpers and common queries for invoice payment
    installments.

    Installments belong to invoices and represent scheduled payment
    parts of a formal billing document.
    """

    @staticmethod
    def get_queryset_for_website(
        *,
        website,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return a tenant-scoped installment queryset.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[PaymentInstallment]:
                Tenant-scoped installment queryset.
        """
        return PaymentInstallment.objects.filter(website=website)

    @classmethod
    def get_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return installments linked to an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose installments should be returned.

        Returns:
            QuerySet[PaymentInstallment]:
                Invoice-scoped installment queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            invoice=invoice
        )

    @classmethod
    def get_paid_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return paid installments for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose paid installments should be returned.

        Returns:
            QuerySet[PaymentInstallment]:
                Paid installment queryset.
        """
        return cls.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).filter(
            paid_at__isnull=False,
            cancelled_at__isnull=True,
        )

    @classmethod
    def get_unpaid_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return unpaid active installments for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose unpaid installments should be returned.

        Returns:
            QuerySet[PaymentInstallment]:
                Unpaid installment queryset.
        """
        return cls.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).filter(
            paid_at__isnull=True,
            cancelled_at__isnull=True,
        )

    @classmethod
    def get_cancelled_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return cancelled installments for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose cancelled installments should be returned.

        Returns:
            QuerySet[PaymentInstallment]:
                Cancelled installment queryset.
        """
        return cls.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).filter(cancelled_at__isnull=False)

    @classmethod
    def get_overdue_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return overdue unpaid installments for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose overdue installments should be returned.

        Returns:
            QuerySet[PaymentInstallment]:
                Overdue installment queryset.
        """
        return cls.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).filter(
            paid_at__isnull=True,
            cancelled_at__isnull=True,
            due_at__lt=timezone.now(),
        )

    @classmethod
    def get_next_unpaid_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> PaymentInstallment | None:
        """
        Return the next unpaid active installment for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose next unpaid installment should be returned.

        Returns:
            PaymentInstallment | None:
                Next unpaid installment if one exists, otherwise None.
        """
        return (
            cls.get_unpaid_queryset_for_invoice(
                website=website,
                invoice=invoice,
            )
            .order_by("sequence_number", "due_at")
            .first()
        )

    @classmethod
    def get_latest_paid_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> PaymentInstallment | None:
        """
        Return the most recently paid installment for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose latest paid installment should be returned.

        Returns:
            PaymentInstallment | None:
                Most recently paid installment if one exists, otherwise
                None.
        """
        return (
            cls.get_paid_queryset_for_invoice(
                website=website,
                invoice=invoice,
            )
            .order_by("-paid_at", "-sequence_number")
            .first()
        )

    @staticmethod
    def is_paid(
        *,
        installment: PaymentInstallment,
    ) -> bool:
        """
        Determine whether an installment is fully paid.

        Args:
            installment:
                Installment to inspect.

        Returns:
            bool:
                True when the installment has a paid timestamp and is
                not cancelled.
        """
        return (
            installment.paid_at is not None
            and installment.cancelled_at is None
        )

    @staticmethod
    def is_cancelled(
        *,
        installment: PaymentInstallment,
    ) -> bool:
        """
        Determine whether an installment is cancelled.

        Args:
            installment:
                Installment to inspect.

        Returns:
            bool:
                True when the installment has a cancellation timestamp.
        """
        return installment.cancelled_at is not None

    @staticmethod
    def is_overdue(
        *,
        installment: PaymentInstallment,
    ) -> bool:
        """
        Determine whether an installment is overdue.

        Args:
            installment:
                Installment to inspect.

        Returns:
            bool:
                True when the installment is unpaid, active, and its
                due time has passed.
        """
        if installment.paid_at is not None:
            return False

        if installment.cancelled_at is not None:
            return False

        return installment.due_at < timezone.now()
    
    @staticmethod
    def get_balance(
        *,
        installment: PaymentInstallment,
    ) -> Decimal:
        """
        Return the remaining unpaid balance for an installment.

        Args:
            installment:
                Installment to inspect.

        Returns:
            Decimal:
                Remaining amount still unpaid.
        """
        balance = installment.amount - installment.amount_paid
        return balance if balance > Decimal("0") else Decimal("0")

    @staticmethod
    def is_partially_paid(
        *,
        installment: PaymentInstallment,
    ) -> bool:
        """
        Determine whether an installment is partially paid.

        Args:
            installment:
                Installment to inspect.

        Returns:
            bool:
                True when some amount has been paid but the installment
                is not yet fully paid or cancelled.
        """
        if installment.cancelled_at is not None:
            return False

        return (
            installment.amount_paid > Decimal("0")
            and installment.amount_paid < installment.amount
        )
    

    @classmethod
    def get_upcoming_queryset_for_invoice(
        cls,
        *,
        website,
        invoice,
        days_ahead: int = 2,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return unpaid active installments due within the upcoming window.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose upcoming installments should be returned.
            days_ahead:
                Number of days ahead to consider upcoming.

        Returns:
            QuerySet[PaymentInstallment]:
                Upcoming installment queryset.
        """
        now = timezone.now()
        cutoff = now + timezone.timedelta(days=days_ahead)

        return cls.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).filter(
            cancelled_at__isnull=True,
            paid_at__isnull=True,
            due_at__gte=now,
            due_at__lte=cutoff,
        )

    @classmethod
    def get_next_due_for_invoice(
        cls,
        *,
        website,
        invoice,
    ) -> PaymentInstallment | None:
        """
        Return the next active unpaid installment due for an invoice.

        Args:
            website:
                Tenant website.
            invoice:
                Invoice whose next due installment should be returned.

        Returns:
            PaymentInstallment | None:
                Next active unpaid installment if one exists, otherwise
                None.
        """
        return (
            cls.get_unpaid_queryset_for_invoice(
                website=website,
                invoice=invoice,
            )
            .order_by("due_at", "sequence_number", "created_at")
            .first()
        )

    @classmethod
    def get_overdue_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[PaymentInstallment]:
        """
        Return overdue unpaid active installments for a tenant.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[PaymentInstallment]:
                Overdue installment queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            cancelled_at__isnull=True,
            paid_at__isnull=True,
            due_at__lt=timezone.now(),
        )