from __future__ import annotations

from rest_framework import serializers


class ReassignmentApprovePoolSerializer(serializers.Serializer):
    """
    Validate reassignment approval back to pool payload.
    """

    internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )