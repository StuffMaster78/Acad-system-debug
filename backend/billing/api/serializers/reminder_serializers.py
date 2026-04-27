from __future__ import annotations

from rest_framework import serializers

from billing.models.reminder import Reminder


class ReminderReadSerializer(serializers.ModelSerializer):
    """
    Serialize reminder records for read operations.

    This serializer is intended for listing and retrieving reminder
    records. It does not perform reminder dispatch or mutation.
    """

    class Meta:
        """
        Configure serializer fields for reminder reads.
        """

        model = Reminder
        fields = [
            "id",
            "invoice",
            "payment_request",
            "channel",
            "event_key",
            "status",
            "scheduled_for",
            "sent_at",
            "failed_at",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class InvoiceReminderCreateSerializer(serializers.Serializer):
    """
    Validate payload for creating an invoice reminder record.
    """

    event_key = serializers.CharField(
        max_length=100,
        required=False,
        default="billing.invoice.reminder",
    )
    channel = serializers.CharField(
        max_length=50,
        required=False,
        default="email",
    )
    scheduled_for = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )


class PaymentRequestReminderCreateSerializer(serializers.Serializer):
    """
    Validate payload for creating a payment request reminder record.
    """

    event_key = serializers.CharField(
        max_length=100,
        required=False,
        default="billing.payment_request.reminder",
    )
    channel = serializers.CharField(
        max_length=50,
        required=False,
        default="email",
    )
    scheduled_for = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )