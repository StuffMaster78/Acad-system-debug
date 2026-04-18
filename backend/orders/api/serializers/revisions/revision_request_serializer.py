from __future__ import annotations

from rest_framework import serializers


class RevisionRequestSerializer(serializers.Serializer):
    """
    Validate revision routing request payload.
    """

    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
    )
    scope_summary = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=4000,
    )
    is_within_original_scope = serializers.BooleanField(
        required=True,
    )