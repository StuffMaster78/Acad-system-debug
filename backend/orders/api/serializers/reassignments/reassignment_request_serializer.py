from __future__ import annotations

from rest_framework import serializers


class ReassignmentRequestSerializer(serializers.Serializer):
    """
    Validate reassignment request payload.
    """

    requester_role = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=32,
    )
    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
    )
    internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )