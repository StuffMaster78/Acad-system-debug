from __future__ import annotations

from rest_framework import serializers


class RouteToStaffingSerializer(serializers.Serializer):
    """
    Validate route to staffing input.

    This action does not currently require a payload, but keeping a
    serializer gives us a stable extension point later.
    """

    pass