from rest_framework import serializers


class EventTimelineSerializer(serializers.Serializer):
    stage = serializers.CharField()
    event_status = serializers.CharField()
    duration_ms = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField()