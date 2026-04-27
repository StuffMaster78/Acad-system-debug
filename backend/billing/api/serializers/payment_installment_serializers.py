from __future__ import annotations

from decimal import Decimal
from rest_framework import serializers

from billing.models.installment import PaymentInstallment


class PaymentInstallmentReadSerializer(serializers.ModelSerializer):
    """
    Serialize invoice payment installments for read operations.
    """

    remaining_amount = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    is_partially_paid = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        """
        Configure serializer fields for installment reads.
        """

        model = PaymentInstallment
        fields = [
            "id",
            "invoice",
            "sequence_number",
            "amount",
            "amount_paid",
            "remaining_amount",
            "due_at",
            "paid_at",
            "cancelled_at",
            "is_paid",
            "is_partially_paid",
            "is_overdue",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

        def get_remaining_amount(self, obj: PaymentInstallment) -> Decimal:
            """
            Return remaining unpaid installment amount.
            """
            balance = obj.amount - obj.amount_paid
            return balance if balance > Decimal("0") else Decimal("0")

        def get_is_paid(self, obj: PaymentInstallment) -> bool:
            """
            Return whether the installment is fully paid.
            """
            return obj.paid_at is not None and obj.cancelled_at is None

        def get_is_partially_paid(self, obj: PaymentInstallment) -> bool:
            """
            Return whether the installment is partially paid.
            """
            if obj.cancelled_at is not None:
                return False
            return obj.amount_paid > Decimal("0") and obj.amount_paid < obj.amount

        def get_is_overdue(self, obj: PaymentInstallment) -> bool:
            """
            Return whether the installment is overdue.
            """
            if obj.cancelled_at is not None or obj.paid_at is not None:
                return False
            from django.utils import timezone
            return obj.due_at < timezone.now()


class PaymentInstallmentCreateItemSerializer(serializers.Serializer):
    """
    Validate a single installment entry within a schedule payload.
    """

    sequence_number = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    due_at = serializers.DateTimeField()


class PaymentInstallmentScheduleCreateSerializer(serializers.Serializer):
    """
    Validate payload for creating an invoice installment schedule.
    """

    schedule = PaymentInstallmentCreateItemSerializer(many=True)


class PaymentInstallmentCancelSerializer(serializers.Serializer):
    """
    Validate payload for cancelling an installment.
    """

    pass