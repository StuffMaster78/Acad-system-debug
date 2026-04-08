from rest_framework import serializers


class RegistrationResendSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RegistrationResendResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()