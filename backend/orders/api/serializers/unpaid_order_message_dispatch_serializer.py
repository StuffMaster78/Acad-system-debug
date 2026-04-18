from __future__ import annotations

from rest_framework import serializers

from orders.models.legacy_models.unpaid_order_message_dispatch import (
    UnpaidOrderMessageDispatch,
)


class UnpaidOrderMessageDispatchSerializer(serializers.ModelSerializer):
    """
    Read serializer for unpaid order reminder dispatch history.
    """

    message_name = serializers.CharField(
        source="unpaid_order_message.name",
        read_only=True,
    )

    class Meta:
        model = UnpaidOrderMessageDispatch
        fields = (
            "id",
            "website",
            "order",
            "unpaid_order_message",
            "message_name",
            "client",
            "recipient_email",
            "subject_snapshot",
            "message_snapshot",
            "status",
            "scheduled_for",
            "attempted_at",
            "sent_at",
            "failed_at",
            "cancelled_at",
            "error_message",
            "created_at",
        )
        read_only_fields = fields