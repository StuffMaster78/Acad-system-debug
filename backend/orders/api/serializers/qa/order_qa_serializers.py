from __future__ import annotations

from rest_framework import serializers


class SubmitOrderForQASerializer(serializers.Serializer):
    """
    Validate writer submission to QA.
    """

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class ApproveOrderForClientDeliverySerializer(serializers.Serializer):
    """
    Validate QA approval before client delivery.
    """

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


class ReturnOrderToWriterSerializer(serializers.Serializer):
    """
    Validate QA return-to-writer payload.
    """

    reason = serializers.CharField(
        required=True,
        allow_blank=False,
    )