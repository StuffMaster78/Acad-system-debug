from __future__ import annotations

from rest_framework import serializers


class ReassignmentApproveAssignSerializer(serializers.Serializer):
    """
    Validate reassignment approval to a specific writer payload.
    """

    writer_id = serializers.IntegerField(min_value=1)
    internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )