from __future__ import annotations

from rest_framework import serializers


class ReassignmentRejectSerializer(serializers.Serializer):
    """
    Validate reassignment rejection payload.
    """

    internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )