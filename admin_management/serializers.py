from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AdminProfile, BlacklistedUser, AdminPromotionRequest,
    AdminActivityLog
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

class AdminLogSerializer(serializers.ModelSerializer):
    admin = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdminActivityLog
        fields = "__all__"
        read_only_fields = fields

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

class AdminLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}}
        }

class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    suspended_users = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_disputes = serializers.IntegerField()
    resolved_disputes = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()

    class Meta:
        fields = [
            "total_users", "active_users", "suspended_users",
            "total_orders", "completed_orders", "pending_orders",
            "total_revenue", "total_disputes", "resolved_disputes",
            "open_tickets", "closed_tickets"
        ]

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
class DashboardSerializer(serializers.Serializer):
    stats = DashboardStatsSerializer()
    recent_activities = AdminLogSerializer(many=True)
    pending_promotion_requests = AdminPromotionRequestSerializer(many=True)

    class Meta:
        fields = ["stats", "recent_activities", "pending_promotion_requests"]

class UserActivitySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    last_login = serializers.DateTimeField()
    total_logins = serializers.IntegerField()
    total_actions = serializers.IntegerField()

    class Meta:
        fields = [
            "user_id", "username", "email",
            "last_login", "total_logins", "total_actions"
        ]


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = fields


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"]
        )
        return user
    



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


class SuspendUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    duration_days = serializers.IntegerField(required=False, min_value=1)
    notify_user = serializers.BooleanField(default=True)
    suspend_orders = serializers.BooleanField(default=False)
    suspend_communications = serializers.BooleanField(default=False)
    suspend_payments = serializers.BooleanField(default=False)
    suspend_profile = serializers.BooleanField(default=True)
    custom_end_date = serializers.DateTimeField(required=False, allow_null=True)
    lift_immediately = serializers.BooleanField(default=False)
    admin_note = serializers.CharField(required=False, allow_blank=True)
    action_reason = serializers.CharField(required=False, allow_blank=True)
    notify_reason = serializers.CharField(required=False, allow_blank=True)
    log_action = serializers.BooleanField(default=True)
    blacklist_user = serializers.BooleanField(default=False)
    blacklist_reason = serializers.CharField(required=False, allow_blank=True)
    blacklist_duration_days = serializers.IntegerField(required=False, min_value=1)
    blacklist_custom_end_date = serializers.DateTimeField(required=False, allow_null=True)
    probation = serializers.BooleanField(default=False)
    probation_reason = serializers.CharField(required=False, allow_blank=True)
    probation_duration_days = serializers.IntegerField(required=False, min_value=1)
    probation_custom_end_date = serializers.DateTimeField(required=False, allow_null=True)
    notify_probation = serializers.BooleanField(default=False)
    probation_end_immediately = serializers.BooleanField(default=False)

    class Meta:
        fields = [
            "user_id", "reason", "duration_days", "notify_user",
            "suspend_orders", "suspend_communications", "suspend_payments",
            "suspend_profile", "custom_end_date", "lift_immediately",
            "admin_note", "action_reason", "notify_reason", "log_action",
            "blacklist_user", "blacklist_reason", "blacklist_duration_days",
            "blacklist_custom_end_date", "probation", "probation_reason",
            "probation_duration_days", "probation_custom_end_date",
            "notify_probation", "probation_end_immediately"
        ]

class LiftSuspensionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    notify_user = serializers.BooleanField(default=True)
    admin_note = serializers.CharField(required=False, allow_blank=True)
    action_reason = serializers.CharField(required=False, allow_blank=True)
    notify_reason = serializers.CharField(required=False, allow_blank=True)
    log_action = serializers.BooleanField(default=True)

    class Meta:
        fields = [
            "user_id", "reason", "notify_user",
            "admin_note", "action_reason", "notify_reason", "log_action"
        ]


class AdminLogSerializer(serializers.ModelSerializer):
    admin = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdminActivityLog
        fields = "__all__"
        read_only_fields = ["id", "timestamp", "admin"]


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


class AdminPromotionRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPromotionRequest
        fields = [
            "requested_role",
            "reason"
        ]
        read_only_fields = [
            "id", "status", "requested_at", "approved_at",
            "rejected_at", "requested_by"
        ]
        extra_kwargs = {
            "requested_role": {"required": True},
            "reason": {"required": False}
        }

