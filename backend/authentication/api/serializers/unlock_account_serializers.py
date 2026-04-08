from rest_framework import serializers


class AccountUnlockRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AccountUnlockConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    otp_code = serializers.CharField()


class AccountUnlockResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()