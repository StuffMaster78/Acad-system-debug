from __future__ import annotations

from rest_framework import serializers

from special_orders.models import (
    SpecialOrderAccessGrant,
    SpecialOrderAccessLog,
    SpecialOrderExternalLink,
    SpecialOrderInstitutionProfile,
    SpecialOrderPlatformAccessVault,
    SpecialOrderTwoFactorRequest,
)


class InstitutionProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderInstitutionProfile
        fields = [
            "id",
            "special_order",
            "institution_name",
            "institution_type",
            "country",
            "state_region",
            "city",
            "program_name",
            "course_code",
            "course_name",
            "instructor_name",
            "term_or_semester",
            "metadata",
            "created_at",
            "updated_at",
        ]


class UpsertInstitutionProfileSerializer(serializers.Serializer):
    institution_name = serializers.CharField(max_length=255)
    institution_type = serializers.CharField(max_length=50)
    country = serializers.CharField(required=False, allow_blank=True)
    state_region = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    program_name = serializers.CharField(required=False, allow_blank=True)
    course_code = serializers.CharField(required=False, allow_blank=True)
    course_name = serializers.CharField(required=False, allow_blank=True)
    instructor_name = serializers.CharField(required=False, allow_blank=True)
    term_or_semester = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.DictField(required=False)


class VaultSafeSerializer(serializers.ModelSerializer):
    """
    Safe vault output.

    Does not expose encrypted_password.
    """

    has_password = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOrderPlatformAccessVault
        fields = [
            "id",
            "special_order",
            "platform",
            "platform_label",
            "login_url",
            "username",
            "has_password",
            "recovery_email",
            "recovery_phone_last4",
            "access_notes",
            "requires_2fa",
            "preferred_2fa_method",
            "preferred_2fa_window_start",
            "preferred_2fa_window_end",
            "timezone",
            "is_active",
            "last_rotated_at",
            "created_by",
            "metadata",
            "created_at",
            "updated_at",
        ]

    def get_has_password(self, obj) -> bool:
        return bool(obj.encrypted_password)


class VaultRevealSerializer(serializers.ModelSerializer):
    """
    Sensitive vault output.

    Only use after service permission check and access logging.
    """

    class Meta:
        model = SpecialOrderPlatformAccessVault
        fields = [
            "id",
            "special_order",
            "platform",
            "platform_label",
            "login_url",
            "username",
            "encrypted_password",
            "recovery_email",
            "recovery_phone_last4",
            "access_notes",
            "requires_2fa",
            "preferred_2fa_method",
            "preferred_2fa_window_start",
            "preferred_2fa_window_end",
            "timezone",
        ]


class CreateVaultSerializer(serializers.Serializer):
    platform = serializers.CharField(max_length=80)
    platform_label = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    login_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    encrypted_password = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    recovery_email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )
    recovery_phone_last4 = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10,
    )
    access_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    requires_2fa = serializers.BooleanField(default=False)
    preferred_2fa_method = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    preferred_2fa_window_start = serializers.TimeField(
        required=False,
        allow_null=True,
    )
    preferred_2fa_window_end = serializers.TimeField(
        required=False,
        allow_null=True,
    )
    timezone_name = serializers.CharField(
        required=False,
        default="UTC",
    )
    metadata = serializers.DictField(required=False)


class ExternalLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderExternalLink
        fields = [
            "id",
            "special_order",
            "label",
            "url",
            "link_type",
            "requires_login",
            "notes",
            "created_by",
            "created_at",
            "updated_at",
        ]


class CreateExternalLinkSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=255)
    url = serializers.URLField(max_length=1000)
    link_type = serializers.CharField(required=False, default="other")
    requires_login = serializers.BooleanField(default=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class AccessGrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderAccessGrant
        fields = [
            "id",
            "vault",
            "special_order",
            "granted_to",
            "granted_by",
            "access_level",
            "reason",
            "expires_at",
            "revoked_at",
            "revoked_by",
            "created_at",
            "updated_at",
        ]


class GrantAccessSerializer(serializers.Serializer):
    granted_to_id = serializers.IntegerField()
    access_level = serializers.CharField(max_length=50)
    reason = serializers.CharField()
    expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderAccessLog
        fields = [
            "id",
            "vault",
            "special_order",
            "accessed_by",
            "action",
            "ip_address",
            "user_agent",
            "metadata",
            "created_at",
        ]


class RevealVaultSerializer(serializers.Serializer):
    access_level = serializers.CharField(max_length=50)


class TwoFactorRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderTwoFactorRequest
        fields = [
            "id",
            "special_order",
            "vault",
            "requested_by",
            "client",
            "status",
            "preferred_method",
            "message",
            "requested_for_time",
            "expires_at",
            "completed_at",
            "code_reference",
            "metadata",
            "created_at",
            "updated_at",
        ]


class CreateTwoFactorRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True)
    requested_for_time = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )


class CompleteTwoFactorRequestSerializer(serializers.Serializer):
    code_reference = serializers.CharField(
        required=False,
        allow_blank=True,
    )