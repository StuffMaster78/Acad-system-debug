from rest_framework import serializers


class GenerateUserMagicLinkResponseSerializer(
    serializers.Serializer
):
    success = serializers.BooleanField()
    user_id = serializers.IntegerField()
    magic_url = serializers.CharField()
    expires_minutes = serializers.IntegerField()


class GenerateUserPasswordResetLinkResponseSerializer(
    serializers.Serializer
):
    success = serializers.BooleanField()
    user_id = serializers.IntegerField()
    reset_link = serializers.CharField()
    otp_code = serializers.CharField()
    token = serializers.CharField()
    expires_hours = serializers.IntegerField()