from rest_framework import serializers


class ImpersonationCreateSerializer(serializers.Serializer):
    target_user_id = serializers.IntegerField()
    reason = serializers.CharField()


class ImpersonationCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    token = serializers.CharField()
    expires_in_hours = serializers.IntegerField()


class ImpersonationStartSerializer(serializers.Serializer):
    token = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True)


class ImpersonationEndSerializer(serializers.Serializer):
    close_tab = serializers.BooleanField(required=False, default=False)
    reason = serializers.CharField(required=False, allow_blank=True)


class ImpersonationUserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.CharField()
    username = serializers.CharField()
    full_name = serializers.CharField(allow_blank=True)
    role = serializers.CharField(allow_null=True, required=False)


class ImpersonationStateSerializer(serializers.Serializer):
    is_impersonation = serializers.BooleanField()
    impersonated_by = serializers.DictField(required=False)
    started_at = serializers.CharField(required=False)


class ImpersonationStartResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = ImpersonationUserInfoSerializer()
    impersonation = ImpersonationStateSerializer()
    expires_in = serializers.IntegerField()


class ImpersonationEndResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False)
    refresh_token = serializers.CharField(required=False)
    user = ImpersonationUserInfoSerializer(required=False)
    message = serializers.CharField()
    close_tab = serializers.BooleanField()


class ImpersonationStatusResponseSerializer(serializers.Serializer):
    is_impersonating = serializers.BooleanField()
    impersonator = serializers.DictField(required=False, allow_null=True)