from django.contrib.auth import get_user_model
from rest_framework import serializers

from admin_management.models import (
    AdminActivityLog,
    AdminProfile,
    AdminPromotionRequest,
    BlacklistedUser,
)
from websites.models.websites import Website

from .user_serializers import (
    CreateUserSerializer,
    UserDetailSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class AdminProfileSerializer(serializers.ModelSerializer):
    """Serialize admin profile permissions and audit metadata."""

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdminProfile
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "updated_at",
            "last_login",
            "last_action",
            "action_count",
        ]


class AdminProfileCreateSerializer(serializers.ModelSerializer):
    """Create an admin profile with scoped permissions."""

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
            "created_at",
            "updated_at",
            "last_login",
            "last_action",
            "action_count",
        ]


class AdminProfileUpdateSerializer(serializers.ModelSerializer):
    """Update admin profile permissions."""

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
            "user",
            "created_at",
            "updated_at",
            "last_login",
            "last_action",
            "action_count",
        ]


class AdminLogSerializer(serializers.ModelSerializer):
    """Serialize admin activity log entries."""

    admin = serializers.StringRelatedField(read_only=True)
    admin_username = serializers.SerializerMethodField()
    admin_id = serializers.SerializerMethodField()

    class Meta:
        model = AdminActivityLog
        fields = [
            "id",
            "admin",
            "admin_id",
            "admin_username",
            "action",
            "timestamp",
        ]
        read_only_fields = fields

    def get_admin_username(self, obj):
        """Return the actor username when the actor still exists."""
        return obj.admin.username if obj.admin else None

    def get_admin_id(self, obj):
        """Return the actor primary key when the actor still exists."""
        return obj.admin_id


class BlacklistedUserSerializer(serializers.ModelSerializer):
    """Serialize a blacklisted user record."""

    blacklisted_by = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    website = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlacklistedUser
        fields = [
            "email",
            "user",
            "website",
            "blacklisted_by",
            "reason",
            "blacklisted_at",
        ]
        read_only_fields = [
            "blacklisted_at",
            "blacklisted_by",
            "user",
            "website",
        ]


class BlacklistedUserDetailSerializer(serializers.ModelSerializer):
    """Serialize blacklist detail responses."""

    blacklisted_by = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    website = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlacklistedUser
        fields = [
            "id",
            "email",
            "user",
            "website",
            "blacklisted_by",
            "reason",
            "blacklisted_at",
        ]
        read_only_fields = fields


class BlacklistedUserListSerializer(serializers.ModelSerializer):
    """Serialize blacklist list responses."""

    blacklisted_by = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    website = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BlacklistedUser
        fields = [
            "id",
            "email",
            "user",
            "website",
            "blacklisted_by",
            "blacklisted_at",
        ]
        read_only_fields = fields


class BlacklistUserSerializer(serializers.Serializer):
    """Validate requests to add an email address to the blacklist."""

    email = serializers.EmailField(required=True)
    website = serializers.PrimaryKeyRelatedField(
        queryset=Website.objects.all()
    )
    reason = serializers.CharField(required=False, allow_blank=True)


class RemoveBlacklistSerializer(serializers.Serializer):
    """Validate requests to remove an email address from the blacklist."""

    email = serializers.EmailField(required=True)


class AdminLoginSerializer(serializers.ModelSerializer):
    """Legacy admin login serializer."""

    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            }
        }


class DashboardStatsSerializer(serializers.Serializer):
    """Serialize dashboard summary counters."""

    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    suspended_users = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    total_disputes = serializers.IntegerField()
    resolved_disputes = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    paid_orders_count = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    unpaid_orders_count = serializers.IntegerField(
        required=False,
        allow_null=True,
    )


class AdminPromotionRequestSerializer(serializers.ModelSerializer):
    """Serialize admin promotion requests."""

    requested_by = serializers.StringRelatedField(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    rejected_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdminPromotionRequest
        fields = "__all__"
        read_only_fields = [
            "id",
            "status",
            "requested_at",
            "approved_at",
            "rejected_at",
            "requested_by",
        ]
        extra_kwargs = {
            "requested_role": {"required": True},
            "reason": {"required": False},
        }


class AdminPromotionRequestCreateSerializer(serializers.ModelSerializer):
    """Validate admin promotion request creation."""

    class Meta:
        model = AdminPromotionRequest
        fields = [
            "requested_role",
            "reason",
        ]
        read_only_fields = [
            "id",
            "status",
            "requested_at",
            "approved_at",
            "rejected_at",
            "requested_by",
        ]
        extra_kwargs = {
            "requested_role": {"required": True},
            "reason": {"required": False},
        }


class DashboardSerializer(serializers.Serializer):
    """Serialize admin dashboard payloads."""

    stats = DashboardStatsSerializer()
    recent_activities = AdminLogSerializer(many=True)
    pending_promotion_requests = AdminPromotionRequestSerializer(many=True)
    total_writers = serializers.IntegerField(required=False, allow_null=True)
    total_editors = serializers.IntegerField(required=False, allow_null=True)
    total_support = serializers.IntegerField(required=False, allow_null=True)
    total_clients = serializers.IntegerField(required=False, allow_null=True)
    suspended_users = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    total_orders = serializers.IntegerField(required=False, allow_null=True)
    orders_by_status = serializers.DictField(required=False, allow_null=True)
    total_revenue = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    paid_orders_count = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    unpaid_orders_count = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    recent_orders_count = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    total_tickets = serializers.IntegerField(required=False, allow_null=True)
    open_tickets_count = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    closed_tickets_count = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    orders_in_progress = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    orders_on_revision = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    disputed_orders = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    amount_paid_today = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    income_this_week = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    income_2weeks = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    income_monthly = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class UserActivitySerializer(serializers.Serializer):
    """Serialize user activity summaries."""

    user_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    last_login = serializers.DateTimeField()
    total_logins = serializers.IntegerField()
    total_actions = serializers.IntegerField()


class AdminPlaceOrderSerializer(serializers.Serializer):
    """Validate admin-created order requests."""

    topic = serializers.CharField(required=True, max_length=255)
    paper_type_id = serializers.IntegerField(required=True)
    number_of_pages = serializers.IntegerField(required=True, min_value=1)
    client_deadline = serializers.DateTimeField(required=True)
    order_instructions = serializers.CharField(required=True)
    academic_level_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    formatting_style_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    subject_id = serializers.IntegerField(required=False, allow_null=True)
    type_of_work_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    english_type_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    number_of_slides = serializers.IntegerField(required=False, default=0)
    number_of_refereces = serializers.IntegerField(required=False, default=0)
    spacing = serializers.CharField(required=False, default="single")
    extra_services = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    preferred_writer_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    discount_code = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    client_id = serializers.IntegerField(required=False, allow_null=True)
    external_contact_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    external_contact_email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    external_contact_phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )
    allow_unpaid_access = serializers.BooleanField(
        required=False,
        default=False,
    )

    def validate(self, attrs):
        """Require either an existing client or external contact details."""
        client_id = attrs.get("client_id")
        external_name = attrs.get("external_contact_name")
        external_email = attrs.get("external_contact_email")

        if not client_id and not (external_name or external_email):
            raise serializers.ValidationError(
                "Provide client_id or external contact details."
            )

        if client_id and (external_name or external_email):
            raise serializers.ValidationError(
                "Do not provide both client_id and external contact details."
            )

        return attrs


class SuspendUserSerializer(serializers.Serializer):
    """Validate account suspension requests."""

    user_id = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    duration_days = serializers.IntegerField(required=False, min_value=1)
    notify_user = serializers.BooleanField(default=True)
    suspend_orders = serializers.BooleanField(default=False)
    suspend_communications = serializers.BooleanField(default=False)
    suspend_payments = serializers.BooleanField(default=False)
    suspend_profile = serializers.BooleanField(default=True)
    custom_end_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    lift_immediately = serializers.BooleanField(default=False)
    admin_note = serializers.CharField(required=False, allow_blank=True)
    action_reason = serializers.CharField(required=False, allow_blank=True)
    notify_reason = serializers.CharField(required=False, allow_blank=True)
    log_action = serializers.BooleanField(default=True)
    blacklist_user = serializers.BooleanField(default=False)
    blacklist_reason = serializers.CharField(required=False, allow_blank=True)
    blacklist_duration_days = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    blacklist_custom_end_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    probation = serializers.BooleanField(default=False)
    probation_reason = serializers.CharField(required=False, allow_blank=True)
    probation_duration_days = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    probation_custom_end_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    notify_probation = serializers.BooleanField(default=False)
    probation_end_immediately = serializers.BooleanField(default=False)


class LiftSuspensionSerializer(serializers.Serializer):
    """Validate suspension lift requests."""

    user_id = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    notify_user = serializers.BooleanField(default=True)
    admin_note = serializers.CharField(required=False, allow_blank=True)
    action_reason = serializers.CharField(required=False, allow_blank=True)
    notify_reason = serializers.CharField(required=False, allow_blank=True)
    log_action = serializers.BooleanField(default=True)


__all__ = [
    "AdminLogSerializer",
    "AdminLoginSerializer",
    "AdminPlaceOrderSerializer",
    "AdminProfileCreateSerializer",
    "AdminProfileSerializer",
    "AdminProfileUpdateSerializer",
    "AdminPromotionRequestCreateSerializer",
    "AdminPromotionRequestSerializer",
    "BlacklistUserSerializer",
    "BlacklistedUserDetailSerializer",
    "BlacklistedUserListSerializer",
    "BlacklistedUserSerializer",
    "CreateUserSerializer",
    "DashboardSerializer",
    "DashboardStatsSerializer",
    "LiftSuspensionSerializer",
    "RemoveBlacklistSerializer",
    "SuspendUserSerializer",
    "UserActivitySerializer",
    "UserDetailSerializer",
    "UserSerializer",
    "UserUpdateSerializer",
]
