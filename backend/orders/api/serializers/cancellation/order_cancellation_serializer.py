from __future__ import annotations

from rest_framework import serializers

from orders.services.order_cancellation_service import (
    OrderCancellationService,
)


class OrderCancelActionSerializer(serializers.Serializer):
    """
    Validate cancellation input for order cancellation actions.
    """

    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=1000,
    )
    refund_destination = serializers.ChoiceField(
        choices=[
            OrderCancellationService.REFUND_DESTINATION_WALLET,
            OrderCancellationService.REFUND_DESTINATION_EXTERNAL,
        ],
        required=True,
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=2000,
        default="",
    )