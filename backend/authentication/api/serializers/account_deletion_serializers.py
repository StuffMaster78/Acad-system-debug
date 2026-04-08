from rest_framework import serializers


class AccountDeletionRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class AccountDeletionConfirmSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()


class CancelDeletionSerializer(serializers.Serializer):
    token = serializers.CharField()


class AccountDeletionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    request_id = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False)
    scheduled_deletion_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    retained_until = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    message = serializers.CharField(
        required=False,
    )

class AccountDeletionStateSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    status = serializers.CharField()
    requested_at = serializers.DateTimeField()
    confirmed_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    scheduled_deletion_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    retained_until = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    completed_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
    )
    reason = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )