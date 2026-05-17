from __future__ import annotations

from rest_framework import serializers


class ReplayEventSerializer(serializers.Serializer):
    """
    Unified timeline event (audit + policy + execution + events).
    """

    type = serializers.CharField()

    event = serializers.CharField(required=False)
    decision = serializers.CharField(required=False)
    event_type = serializers.CharField(required=False)

    risk_score = serializers.FloatField(required=False)

    time = serializers.DateTimeField()


class CommandReplaySerializer(serializers.Serializer):
    command_id = serializers.UUIDField()
    timeline = ReplayEventSerializer(many=True)