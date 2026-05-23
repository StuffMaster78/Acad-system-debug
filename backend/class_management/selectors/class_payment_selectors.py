from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import (
    ClassInstallment,
    ClassInvoiceLink,
    ClassPaymentAllocation,
)


class ClassPaymentSelector:
    """
    Read/query helpers for class payments and payment milestones.
    """

    @staticmethod
    def allocations_for_order(
        *,
        class_order,
    ) -> QuerySet[ClassPaymentAllocation]:
        return ClassPaymentAllocation.objects.filter(
            class_order=class_order,
        ).order_by("-applied_at")

    @staticmethod
    def invoice_links_for_order(
        *,
        class_order,
    ) -> QuerySet[ClassInvoiceLink]:
        return ClassInvoiceLink.objects.filter(
            class_order=class_order,
        ).order_by("-created_at")

    @staticmethod
    def payment_milestones_for_order(
        *,
        class_order,
    ) -> QuerySet[ClassInstallment]:
        return ClassInstallment.objects.filter(
            plan__class_order=class_order,
        ).order_by("due_at")

    @staticmethod
    def installments_for_order(
        *,
        class_order,
    ) -> QuerySet[ClassInstallment]:
        """Compatibility alias for existing installment callers."""
        return ClassPaymentSelector.payment_milestones_for_order(
            class_order=class_order,
        )

    @staticmethod
    def overdue_payment_milestones(*, website) -> QuerySet[ClassInstallment]:
        return (
            ClassInstallment.objects.filter(
                plan__class_order__website=website,
                status="overdue",
            )
            .select_related("plan", "plan__class_order")
            .order_by("due_at")
        )

    @staticmethod
    def overdue_installments(*, website) -> QuerySet[ClassInstallment]:
        """Compatibility alias for existing installment callers."""
        return ClassPaymentSelector.overdue_payment_milestones(
            website=website,
        )
