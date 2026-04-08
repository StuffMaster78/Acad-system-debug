from rest_framework import serializers


class RegistrationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)


class RegistrationConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    otp_code = serializers.CharField()


class RegistrationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    user_id = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)