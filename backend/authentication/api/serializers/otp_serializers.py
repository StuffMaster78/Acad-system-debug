from rest_framework import serializers


class OTPCreateRequestSerializer(serializers.Serializer):
    purpose = serializers.CharField()


class OTPCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    otp_id = serializers.IntegerField()
    purpose = serializers.CharField()
    expires_at = serializers.DateTimeField()
    raw_code = serializers.CharField(required=False)


class OTPVerifySerializer(serializers.Serializer):
    purpose = serializers.CharField()
    code = serializers.CharField()


class OTPVerifyResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    purpose = serializers.CharField()
    verified = serializers.BooleanField()


class OTPListItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    purpose = serializers.CharField()
    expires_at = serializers.DateTimeField()
    used_at = serializers.DateTimeField(allow_null=True)
    attempts = serializers.IntegerField()
    max_attempts = serializers.IntegerField()
    created_at = serializers.DateTimeField()