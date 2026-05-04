from __future__ import annotations

from rest_framework import serializers

from class_management.models import (
    ClassAccessGrant,
    ClassAccessLog,
    ClassTwoFactorRequest,
    ClassTwoFactorWindow,
)


class ClassAccessDetailWriteSerializer(serializers.Serializer):
    institution_name = serializers.CharField(required=False, allow_blank=True)
    institution_state = serializers.CharField(required=False, allow_blank=True)
    class_portal_url = serializers.URLField(required=False, allow_blank=True)
    class_name = serializers.CharField(required=False, allow_blank=True)
    class_code = serializers.CharField(required=False, allow_blank=True)
    login_username = serializers.CharField(required=False, allow_blank=True)
    login_password = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    requires_two_factor = serializers.BooleanField(default=False)
    two_factor_method = serializers.CharField(required=False, allow_blank=True)
    preferred_contact_method = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    extra_login_notes = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ClassAccessDetailReadSerializer(serializers.Serializer):
    institution_name = serializers.CharField()
    institution_state = serializers.CharField()
    class_portal_url = serializers.URLField()
    class_name = serializers.CharField()
    class_code = serializers.CharField()
    login_username = serializers.CharField()
    login_password = serializers.CharField()
    requires_two_factor = serializers.BooleanField()
    two_factor_method = serializers.CharField()
    preferred_contact_method = serializers.CharField()
    extra_login_notes = serializers.CharField()
    emergency_contact_notes = serializers.CharField()
    two_factor_windows = serializers.ListField()


class ClassTwoFactorWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTwoFactorWindow
        fields = [
            "id",
            "weekday",
            "starts_at",
            "ends_at",
            "timezone",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReplaceTwoFactorWindowsSerializer(serializers.Serializer):
    windows = ClassTwoFactorWindowSerializer(many=True)


class ClassAccessGrantSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassAccessGrant
        fields = "__all__"
        read_only_fields = [
            "status",
            "granted_by",
            "granted_at",
            "revoked_at",
        ]


class GrantAccessSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)


class RevokeAccessSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)


class ViewAccessSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class ClassAccessLogSerializer(serializers.ModelSerializer):
    viewed_by_name = serializers.CharField(
        source="viewed_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassAccessLog
        fields = "__all__"


class ClassTwoFactorRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTwoFactorRequest
        fields = "__all__"
        read_only_fields = [
            "requested_by",
            "requested_at",
            "resolved_at",
        ]


class RequestTwoFactorSerializer(serializers.Serializer):
    needed_by = serializers.DateTimeField(required=False, allow_null=True)
    request_notes = serializers.CharField(required=False, allow_blank=True)


class ResolveTwoFactorSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)