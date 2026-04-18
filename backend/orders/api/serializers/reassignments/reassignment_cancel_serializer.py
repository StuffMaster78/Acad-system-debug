from __future__ import annotations

from rest_framework import serializers


class ReassignmentCancelSerializer(serializers.Serializer):
    """
    Validate reassignment cancel payload.

    No payload is required right now.
    """

    pass