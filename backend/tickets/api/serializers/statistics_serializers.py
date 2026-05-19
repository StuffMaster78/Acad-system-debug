from __future__ import annotations

from rest_framework import serializers

from tickets.models import TicketStatistics


class TicketStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketStatistics
        fields = [
            "website",
            "total_tickets",
            "resolved_tickets",
            "average_resolution_time",
            "created_at",
        ]
        read_only_fields = fields
