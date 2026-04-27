from __future__ import annotations

from decimal import Decimal
from typing import Any

from rest_framework import serializers

from billing.api.serializers.payment_installment_serializers import (
    PaymentInstallmentReadSerializer,
)
from billing.models.invoice import Invoice
from billing.models.installment import PaymentInstallment
from billing.selectors.payment_installment_selectors import (
    PaymentInstallmentSelector,
)


class InvoiceSummarySerializer(serializers.ModelSerializer):
    """
    Serialize a client-safe invoice summary with installment progress.

    This serializer is intended for client-facing invoice visibility.
    It exposes high-level payment progress and installment schedule
    details without exposing internal-only fields.
    """

    installments = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()
    is_fully_paid = serializers.SerializerMethodField()
    next_installment = serializers.SerializerMethodField()

    class Meta:
        """
        Configure serializer fields for client invoice summary reads.
        """

        model = Invoice
        fields = [
            "id",
            "reference",
            "title",
            "description",
            "amount",
            "currency",
            "status",
            "due_at",
            "issued_at",
            "paid_at",
            "installments",
            "total_paid",
            "remaining_balance",
            "is_fully_paid",
            "next_installment",
        ]
        read_only_fields = fields

    def _get_installments(self, obj: Invoice) -> list[PaymentInstallment]:
        """
        Return ordered installments for the invoice.

        Args:
            obj:
                Invoice instance being serialized.

        Returns:
            list[PaymentInstallment]:
                Ordered installment list.
        """
        return list(
            PaymentInstallmentSelector.get_queryset_for_invoice(
                website=obj.website,
                invoice=obj,
            ).order_by("sequence_number", "due_at", "created_at")
        )

    def get_installments(self, obj: Invoice) -> Any:
        """
        Serialize installments for the invoice.

        Args:
            obj:
                Invoice instance being serialized.

        Returns:
            Any:
                Serialized installment data.
        """
        installments = self._get_installments(obj)
        return PaymentInstallmentReadSerializer(
            installments,
            many=True,
        ).data

    def get_total_paid(self, obj: Invoice) -> Decimal:
        """
        Return total amount paid across installments.

        Args:
            obj:
                Invoice instance being serialized.

        Returns:
            Decimal:
                Total allocated installment amount.
        """
        installments = self._get_installments(obj)
        total_paid = sum(
            (installment.amount_paid for installment in installments),
            Decimal("0.00"),
        )
        return total_paid

    def get_remaining_balance(self, obj: Invoice) -> Decimal:
        """
        Return remaining unpaid invoice balance.

        Args:
            obj:
                Invoice instance being serialized.

        Returns:
            Decimal:
                Remaining invoice balance.
        """
        total_paid = self.get_total_paid(obj)
        balance = obj.amount - total_paid
        return balance if balance > Decimal("0.00") else Decimal("0.00")

    def get_is_fully_paid(self, obj: Invoice) -> bool:
        """
        Return whether the invoice is fully paid.

        Args:
            obj:
                Invoice instance being serialized.

        Returns:
            bool:
                True when the invoice is fully paid.
        """
        return self.get_remaining_balance(obj) == Decimal("0.00")

    def get_next_installment(self, obj: Invoice) -> Any:
        """
        Return the next unpaid active installment.

        Args:
            obj:
                Invoice instance being serialized.

        Returns:
            Any:
                Serialized next installment or None if all are paid.
        """
        installment = PaymentInstallmentSelector.get_next_due_for_invoice(
            website=obj.website,
            invoice=obj,
        )
        if installment is None:
            return None

        return PaymentInstallmentReadSerializer(installment).data