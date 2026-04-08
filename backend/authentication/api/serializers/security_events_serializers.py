from rest_framework import serializers


class SecurityEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    event_type = serializers.CharField()
    severity = serializers.CharField()
    ip_address = serializers.CharField(allow_null=True)
    location = serializers.CharField(allow_null=True)
    device = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()