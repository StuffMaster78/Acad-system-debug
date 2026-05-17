from rest_framework import serializers


class EventReplaySerializer(serializers.Serializer):
    event_id = serializers.UUIDField()
    reason = serializers.CharField(required=False, allow_blank=True)