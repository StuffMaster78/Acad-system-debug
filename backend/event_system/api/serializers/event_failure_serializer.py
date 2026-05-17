from rest_framework import serializers


class EventFailureSerializer(serializers.Serializer):
    event_id = serializers.CharField()
    attempts = serializers.IntegerField()
    last_error = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    updated_at = serializers.DateTimeField(allow_null=True)