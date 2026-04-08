from rest_framework import serializers


class LockoutStatusResponseSerializer(serializers.Serializer):
    is_locked = serializers.BooleanField()
    locked_until = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    remaining_seconds = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )