from rest_framework import serializers
from rest_framework import serializers

class MFAStateResponseSerializer(serializers.Serializer):
    required = serializers.BooleanField()
    preferred_method = serializers.CharField(
        allow_null=True,
        required=False,
    )
    available_methods = serializers.ListField(
        child=serializers.CharField(),
    )
    device_count = serializers.IntegerField()


class MFAChallengeResponseSerializer(serializers.Serializer):
    required = serializers.BooleanField()
    status = serializers.CharField()
    method = serializers.CharField(required=False)
    device_id = serializers.IntegerField(required=False)
    device_name = serializers.CharField(required=False, allow_null=True)
    challenge_id = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)
    delivery = serializers.DictField(required=False)
    raw_code = serializers.CharField(required=False)


class MFAVerifyResponseSerializer(serializers.Serializer):
    verified = serializers.BooleanField()
    method = serializers.CharField()
    device_id = serializers.IntegerField()
    device_name = serializers.CharField(allow_null=True)
    challenge_id = serializers.IntegerField(required=False)


class MFADeviceListItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(allow_blank=True, allow_null=True)
    method = serializers.CharField()
    is_active = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    is_primary = serializers.BooleanField(required=False)

class MFAChallengeRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    device_id = serializers.IntegerField(required=False)


class MFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    device_id = serializers.IntegerField(required=False)


class MFADeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()


class MFARegisterDeviceSerializer(serializers.Serializer):
    method = serializers.CharField()
    name = serializers.CharField()
    secret = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_primary = serializers.BooleanField(required=False, default=False)


class MFASetPrimaryDeviceSerializer(serializers.Serializer):
    device_id = serializers.IntegerField()


class MFAVerifyDeviceSerializer(serializers.Serializer):
    device_id = serializers.IntegerField()
    code = serializers.CharField()

    
class MFAVerifyDeviceResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    device_id = serializers.IntegerField()
    message = serializers.CharField()

class MFAToggleDeviceSerializer(serializers.Serializer):
    device_id = serializers.IntegerField()


class BackupCodeGenerateRequestSerializer(serializers.Serializer):
    count = serializers.IntegerField(required=False, min_value=1, max_value=20)


class BackupCodeGenerateResponseSerializer(serializers.Serializer):
    codes = serializers.ListField(child=serializers.CharField())


class BackupCodeUseSerializer(serializers.Serializer):
    code = serializers.CharField()