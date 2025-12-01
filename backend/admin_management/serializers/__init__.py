from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import (
    AdminProfile, BlacklistedUser, AdminPromotionRequest,
    AdminActivityLog
)
from .user_serializers import (
    UserSerializer,  # Use the comprehensive UserSerializer from user_serializers.py
    UserDetailSerializer,
    CreateUserSerializer,
    UserUpdateSerializer,
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
    admin_username = serializers.SerializerMethodField()
    admin_id = serializers.SerializerMethodField()

    class Meta:
        model = AdminActivityLog
        fields = ["id", "admin", "admin_id", "admin_username", "action", "timestamp"]
        read_only_fields = ["id", "timestamp", "admin", "admin_id", "admin_username"]
    
    def get_admin_username(self, obj):
        """Safely get admin username."""
        try:
            if obj.admin:
                return obj.admin.username
        except Exception:
            pass
        return None
    
    def get_admin_id(self, obj):
        """Get admin ID."""
        try:
            if obj.admin:
                return obj.admin.id
        except Exception:
            pass
        return None

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
    paid_orders_count = serializers.IntegerField(required=False, allow_null=True)
    unpaid_orders_count = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        fields = [
            "total_users", "active_users", "suspended_users",
            "total_orders", "completed_orders", "pending_orders",
            "total_revenue", "total_disputes", "resolved_disputes",
            "open_tickets", "closed_tickets",
            "paid_orders_count", "unpaid_orders_count"
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
    # User statistics - flat fields for easy access
    total_writers = serializers.IntegerField(required=False, allow_null=True)
    total_editors = serializers.IntegerField(required=False, allow_null=True)
    total_support = serializers.IntegerField(required=False, allow_null=True)
    total_clients = serializers.IntegerField(required=False, allow_null=True)
    suspended_users = serializers.IntegerField(required=False, allow_null=True)
    # Additional flat fields for compatibility
    total_orders = serializers.IntegerField(required=False, allow_null=True)
    orders_by_status = serializers.DictField(required=False, allow_null=True)
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    paid_orders_count = serializers.IntegerField(required=False, allow_null=True)
    unpaid_orders_count = serializers.IntegerField(required=False, allow_null=True)
    recent_orders_count = serializers.IntegerField(required=False, allow_null=True)
    total_tickets = serializers.IntegerField(required=False, allow_null=True)
    open_tickets_count = serializers.IntegerField(required=False, allow_null=True)
    closed_tickets_count = serializers.IntegerField(required=False, allow_null=True)
    orders_in_progress = serializers.IntegerField(required=False, allow_null=True)
    orders_on_revision = serializers.IntegerField(required=False, allow_null=True)
    disputed_orders = serializers.IntegerField(required=False, allow_null=True)
    amount_paid_today = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    income_this_week = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    income_2weeks = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    income_monthly = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    class Meta:
        fields = [
            "stats", "recent_activities", "pending_promotion_requests",
            "total_writers", "total_editors", "total_support", "total_clients", "suspended_users",
            "total_orders", "orders_by_status", "total_revenue",
            "paid_orders_count", "unpaid_orders_count", "recent_orders_count",
            "total_tickets", "open_tickets_count", "closed_tickets_count",
            "orders_in_progress", "orders_on_revision", "disputed_orders",
            "amount_paid_today", "income_this_week", "income_2weeks", "income_monthly"
        ]

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


# OLD UserSerializer removed - now using UserSerializer from user_serializers.py
# This old serializer only had basic fields and was overriding the comprehensive one
# If you need the old basic serializer, use UserListSerializer from user_serializers.py


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
    


class AdminPlaceOrderSerializer(serializers.Serializer):
    """Serializer for admin placing orders with optional attribution."""
    # Required fields
    topic = serializers.CharField(required=True, max_length=255)
    paper_type_id = serializers.IntegerField(required=True)
    number_of_pages = serializers.IntegerField(required=True, min_value=1)
    client_deadline = serializers.DateTimeField(required=True)
    order_instructions = serializers.CharField(required=True)
    
    # Optional order fields
    academic_level_id = serializers.IntegerField(required=False, allow_null=True)
    formatting_style_id = serializers.IntegerField(required=False, allow_null=True)
    subject_id = serializers.IntegerField(required=False, allow_null=True)
    type_of_work_id = serializers.IntegerField(required=False, allow_null=True)
    english_type_id = serializers.IntegerField(required=False, allow_null=True)
    number_of_slides = serializers.IntegerField(required=False, default=0)
    number_of_refereces = serializers.IntegerField(required=False, default=0)
    spacing = serializers.CharField(required=False, default='single')
    extra_services = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    preferred_writer_id = serializers.IntegerField(required=False, allow_null=True)
    discount_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Attribution options
    client_id = serializers.IntegerField(required=False, allow_null=True, help_text="Attach order to existing client. Leave null for unattributed.")
    external_contact_name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    external_contact_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    external_contact_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    
    # Unpaid visibility override
    allow_unpaid_access = serializers.BooleanField(required=False, default=False, help_text="Allow access even if unpaid")
    
    def validate(self, attrs):
        """Validate that either client_id or external contact info is provided."""
        client_id = attrs.get('client_id')
        external_name = attrs.get('external_contact_name')
        external_email = attrs.get('external_contact_email')
        
        if not client_id and not (external_name or external_email):
            raise serializers.ValidationError(
                "Either 'client_id' must be provided for attributed orders, "
                "or 'external_contact_name'/'external_contact_email' must be provided for unattributed orders."
            )
        
        if client_id and (external_name or external_email):
            raise serializers.ValidationError(
                "Cannot provide both 'client_id' and external contact information. "
                "Use 'client_id' for attributed orders, or external contact for unattributed orders."
            )
        
        return attrs


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


# Duplicate AdminLogSerializer removed - using the one above with admin_username field


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
