from rest_framework import serializers


class DeviceFingerprintSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fingerprint_hash = serializers.CharField()
    device_name = serializers.CharField(allow_null=True)
    ip_address = serializers.CharField(allow_null=True)
    is_trusted = serializers.BooleanField()
    last_seen_at = serializers.DateTimeField()


class TrustDeviceSerializer(serializers.Serializer):
    fingerprint_hash = serializers.CharField()


class UntrustDeviceSerializer(serializers.Serializer):
    fingerprint_hash = serializers.CharField()