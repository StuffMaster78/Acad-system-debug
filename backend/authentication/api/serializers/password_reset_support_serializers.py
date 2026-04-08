from rest_framework import serializers


class PasswordResetValidateTokenSerializer(
    serializers.Serializer
    ):
    token = serializers.CharField()


class PasswordResetValidateTokenResponseSerializer(
    serializers.Serializer
    ):
    valid = serializers.BooleanField()
    message = serializers.CharField(required=False)