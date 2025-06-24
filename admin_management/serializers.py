from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AdminProfile, BlacklistedUser, AdminPromotionRequest
)

User = get_user_model()


class AdminProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdminProfile
        fields = "__all__"
        read_only_fields = [
            "created_at", "updated_at", "last_login",
            "last_action", "action_count"
        ]


class AdminProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = [
            "user",
            "can_manage_users",
            "can_suspend_users",
            "can_put_on_probation",
            "can_handle_orders",
            "can_resolve_disputes",
            "can_manage_payouts",
            "can_manage_financials",
            "can_manage_tickets",
            "can_view_reports",
            "can_blacklist_users",
            "can_manage_writers",
            "can_manage_clients",
            "can_manage_editors",
        ]
        read_only_fields = [
            "created_at", "updated_at", "last_login",
            "last_action", "action_count"
        ]


class AdminProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = [
            "can_manage_users",
            "can_suspend_users",
            "can_put_on_probation",
            "can_handle_orders",
            "can_resolve_disputes",
            "can_manage_payouts",
            "can_manage_financials",
            "can_manage_tickets",
            "can_view_reports",
            "can_blacklist_users",
            "can_manage_writers",
            "can_manage_clients",
            "can_manage_editors",
        ]
        read_only_fields = [
            "user", "created_at", "updated_at",
            "last_login", "last_action", "action_count"
        ]


class BlacklistedUserSerializer(serializers.ModelSerializer):
    blacklisted_by = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    website = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlacklistedUser
        fields = [
            "email", "user", "website",
            "blacklisted_by", "reason", "blacklisted_at"
        ]
        read_only_fields = [
            "blacklisted_at", "blacklisted_by",
            "user", "website"
        ]


class BlacklistUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    website = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class RemoveBlacklistSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class BlacklistedUserDetailSerializer(serializers.ModelSerializer):
    blacklisted_by = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    website = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlacklistedUser
        fields = [
            "id", "email", "user", "website",
            "blacklisted_by", "reason", "blacklisted_at"
        ]
        read_only_fields = fields


class BlacklistedUserListSerializer(serializers.ModelSerializer):
    blacklisted_by = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    website = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlacklistedUser
        fields = [
            "id", "email", "user", "website",
            "blacklisted_by", "blacklisted_at"
        ]
        read_only_fields = fields


class AdminPromotionRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    rejected_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdminPromotionRequest
        fields = "__all__"
        read_only_fields = [
            "id", "status", "requested_at", "approved_at",
            "rejected_at", "requested_by"
        ]
        extra_kwargs = {
            "requested_role": {"required": True},
            "reason": {"required": False}
        }
