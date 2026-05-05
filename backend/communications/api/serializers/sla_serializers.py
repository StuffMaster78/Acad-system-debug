from __future__ import annotations

from rest_framework import serializers

from communications.models.sla import CommunicationThreadSLA


class CommunicationThreadSLASerializer(serializers.ModelSerializer):
    """
    Read serializer for thread SLA records.
    """

    class Meta:
        model = CommunicationThreadSLA
        fields = [
            "id",
            "website",
            "thread",
            "first_response_due_at",
            "next_response_due_at",
            "last_client_response_at",
            "last_writer_response_at",
            "last_staff_response_at",
            "is_breached",
            "breached_at",
        ]
        read_only_fields = fields