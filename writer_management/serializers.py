from rest_framework import serializers
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal
from writer_management.models.order_dispute import OrderDispute
from writer_management.models import (
    WebhookSettings, WebhookPlatform
)
from orders.order_enums import WebhookEvent
from writer_management.models.levels import (
    WriterLevel, WriterLevelHistory
)
from writer_management.models.configs import WriterConfig
from writer_management.models.messages import (
    WriterMessageThread, WriterMessage
)
from writer_management.models.tipping import Tip
from orders.models import Order
from models.payout import WriterPayment, WriterPayoutPreference
from writer_management.models.profile import WriterProfile
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake, WriterDeadlineExtensionRequest,
    WriterOrderHoldRequest, WriterOrderReopenRequest
)
from writer_management.models.performance import (
    WriterPerformanceReport, WriterAutoRanking, WriterReward,
    WriterRewardCriteria, WriterEarningsHistory, WriterEarningsReviewRequest,
)
from writer_management.models.tickets import (
    WriterSupportTicket, WriterDeadlineExtensionRequest,
    WriterOrderHoldRequest, WriterOrderReopenRequest
)
from writer_management.models.discipline import (
    Probation, WriterPenalty, WriterSuspension
)
from writer_management.models.logs import (
    WriterActivityLog, WriterIPLog, WriterRatingCooldown,
    WriterFileDownloadLog
)
from writer_management.models.logs import WriterActionLog
from writer_management.models.profile import WriterProfile
from writer_management.models.requests import WriterOrderRequest, WriterOrderTake
from writer_management.models.configs import WriterConfig
from writer_management.models.tipping import Tip
from writer_management.models.payout import WriterPayoutPreference
# from writer_management.models.webhook import WebhookSettings, WebhookPlatform
from writer_management.models.payout import CurrencyConversionRate
from writer_management.models.performance_snapshot import WriterPerformanceSnapshot
from writer_management.models.writer_warnings import WriterWarning
from writer_management.models.status import WriterStatus
from writer_management.services.status_service import WriterStatusService
from writer_management.models.badges import WriterBadge
from websites.models import Website


User = get_user_model()


### ---------------- Writer Profile Serializers ---------------- ###

class WriterProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Profile
    """
    average_rating = serializers.ReadOnlyField()
    total_ratings = serializers.ReadOnlyField()
    leave_status = serializers.ReadOnlyField()
    wallet_balance = serializers.ReadOnlyField()

    class Meta:
        model = WriterProfile
        fields = '__all__'


class WriterLevelSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Levels
    """
    class Meta:
        model = WriterLevel
        fields = '__all__'


### ---------------- Writer Order Management Serializers ---------------- ###

class WriterOrderRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Order Requests (Express Interest in an Order)
    """
    writer = serializers.PrimaryKeyRelatedField(queryset=WriterProfile.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = WriterOrderRequest
        fields = '__all__'

    def validate(self, data):
        """
        Validate max requests per writer before allowing a new request.
        """
        config = WriterConfig.objects.first()
        if not config:
            raise ValidationError("WriterConfig settings are missing.")

        max_requests = config.max_requests_per_writer
        active_requests = WriterOrderRequest.objects.filter(
            writer=data['writer'],
            approved=False
        ).count()

        if active_requests >= max_requests:
            raise ValidationError(
                f"Writer {data['writer'].user.username} has reached their max request limit."
            )

        return data


class WriterOrderTakeSerializer(serializers.ModelSerializer):
    """
    Serializer for Writers Taking Orders Directly (If Admin Allows)
    """
    writer = serializers.PrimaryKeyRelatedField(queryset=WriterProfile.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = WriterOrderTake
        fields = '__all__'

    def validate(self, data):
        """
        Validate if a writer is allowed to take an order based on config and limits.
        """
        config = WriterConfig.objects.first()
        if not config or not config.takes_enabled:
            raise ValidationError(
                "Order takes are currently disabled. Writers must request orders."
            )

        max_allowed_orders = data['writer'].writer_level.max_orders if data['writer'].writer_level else 0
        current_taken_orders = WriterOrderTake.objects.filter(writer=data['writer']).count()

        if current_taken_orders >= max_allowed_orders:
            raise ValidationError(f"Writer {data['writer'].user.username} has reached their max take limit.")

        return data


class WriterConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin-Controlled Writer Settings
    """
    class Meta:
        model = WriterConfig
        fields = '__all__'


### ---------------- Writer Payment & Earnings Serializers ---------------- ###

class WriterPayoutPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterPayoutPreference
        fields = ["id", "writer", "preferred_method", "payout_threshold",
                  "account_details", "verified", "allowed_currencies"
        ]
        read_only_fields = ["id", "writer", "verified"] 


class WriterPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Payments
    """
    class Meta:
        model = WriterPayment
        fields = '__all__'


class WriterEarningsHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Earnings History
    """
    class Meta:
        model = WriterEarningsHistory
        fields = '__all__'


class WriterEarningsReviewRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Earnings Review Requests
    """
    class Meta:
        model = WriterEarningsReviewRequest
        fields = '__all__'


### ---------------- Writer Performance & Ranking Serializers ---------------- ###

class WriterPerformanceReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Performance Reports
    """
    class Meta:
        model = WriterPerformanceReport
        fields = '__all__'


class WriterAutoRankingSerializer(serializers.ModelSerializer):
    """
    Serializer for Auto-Promotion & Demotion
    """
    class Meta:
        model = WriterAutoRanking
        fields = '__all__'


class WriterRewardSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Rewards
    """
    class Meta:
        model = WriterReward
        fields = '__all__'


class WriterRewardCriteriaSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Reward Criteria
    """
    class Meta:
        model = WriterRewardCriteria
        fields = '__all__'


### ---------------- Writer Penalties & Actions Serializers ---------------- ###

class ProbationSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Probation
    """
    class Meta:
        model = Probation
        fields = '__all__'


class WriterPenaltySerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Penalties
    """
    class Meta:
        model = WriterPenalty
        fields = '__all__'


class WriterSuspensionSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Suspensions
    """
    class Meta:
        model = WriterSuspension
        fields = '__all__'


class WriterActionLogSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Actions (Warnings, Suspensions, etc.)
    """
    class Meta:
        model = WriterActionLog
        fields = '__all__'


### ---------------- Writer Support & Requests Serializers ---------------- ###

class WriterSupportTicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Support Tickets
    """
    class Meta:
        model = WriterSupportTicket
        fields = '__all__'


class WriterDeadlineExtensionRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Deadline Extension Requests
    """
    class Meta:
        model = WriterDeadlineExtensionRequest
        fields = '__all__'


class WriterOrderHoldRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Order Hold Requests
    """
    class Meta:
        model = WriterOrderHoldRequest
        fields = '__all__'


class WriterOrderReopenRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Order Reopen Requests
    """
    class Meta:
        model = WriterOrderReopenRequest
        fields = '__all__'


### ---------------- Writer Activity Serializers ---------------- ###

class WriterActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Activity Logs
    """
    class Meta:
        model = WriterActivityLog
        fields = '__all__'


class WriterIPLogSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer IP Logs
    """
    class Meta:
        model = WriterIPLog
        fields = '__all__'


class WriterRatingCooldownSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Rating Cooldown
    """
    class Meta:
        model = WriterRatingCooldown
        fields = '__all__'


class WriterFileDownloadLogSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer File Download Logs
    """
    class Meta:
        model = WriterFileDownloadLog
        fields = '__all__'


class OrderDisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDispute
        fields = '__all__'

class WriterMessageThreadSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Message Threads
    """
    class Meta:
        model = WriterMessageThread
        fields = '__all__'


class WriterMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Messages
    """
    thread = serializers.PrimaryKeyRelatedField(queryset=WriterMessageThread.objects.all())

    class Meta:
        model = WriterMessage
        fields = '__all__'

class WebhookSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookSettings
        fields = [
            "id",
            "platform",
            "webhook_url",
            "enabled",
            "subscribed_events",
            "is_active",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

    def validate_platform(self, value):
        if value not in WebhookPlatform.values:
            raise serializers.ValidationError("Invalid platform selected.")
        return value

    def validate_subscribed_events(self, value):
        invalid = [v for v in value if v not in WebhookEvent.values]
        if invalid:
            raise serializers.ValidationError(f"Invalid events: {', '.join(invalid)}")
        return value


class TipCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a tip for a writer.
    This serializer handles the creation of a tip, including validation
    of the tip amount and linking it to the writer and order.
    """
    writer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="writer"), source="writer"
    )
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order"
    )
    tip_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tip_reason = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Tip
        fields = [
            "writer_id", "order_id", "tip_amount",
            "tip_reason"
        ]

    def validate_tip_amount(self, value):
        """
        Validate the tip amount to ensure it is greater than zero.
        """
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Tip amount must be greater than zero.")
        return value

    def create(self, validated_data):
        """
        Create a new tip instance using the validated data.
        This method uses the TipService to handle the business logic
        of creating a tip, including calculating the split between
        the writer and the platform.
        """
        from writer_management.services.tip_service import TipService
        request = self.context["request"]
        user = request.user
        website = request.website  # if using custom middleware

        return TipService.create_tip(
            client=user,
            website=website,
            **validated_data
        )
    

class TipListSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source="writer.get_full_name", read_only=True)
    client_name = serializers.CharField(source="client.get_full_name", read_only=True)
    order_title = serializers.CharField(source="order.title", read_only=True)

    class Meta:
        model = Tip
        fields = [
            "id", "tip_amount", "tip_reason", "sent_at",
            "writer_name", "client_name", "order_title",
            "writer_earning", "platform_profit"
        ]

class CurrencyConversionRateSerializer(serializers.ModelSerializer):
    website_id = serializers.PrimaryKeyRelatedField(
        source="website",
        queryset=Website.objects.all()
    )

    class Meta:
        model = CurrencyConversionRate
        fields = [
            "id",
            "website_id",
            "target_currency",
            "rate",
            "effective_date",
            "created_at",
        ]
        read_only_fields = ["created_at"]

class WriterPaymentSerializer(serializers.ModelSerializer):
    writer_id = serializers.PrimaryKeyRelatedField(
        source="writer", queryset=WriterProfile.objects.all()
    )
    website_id = serializers.PrimaryKeyRelatedField(
        source="website", queryset=Website.objects.all()
    )

    class Meta:
        model = WriterPayment
        fields = [
            "id",
            "writer_id",
            "website_id",
            "amount",
            "bonuses",
            "fines",
            "tips",
            "converted_amount",
            "conversion_rate",
            "currency",
            "payment_date",
            "description",
        ]
        read_only_fields = [
            "converted_amount",
            "conversion_rate",
            "currency",
            "payment_date",
        ]



class WriterStatusSerializer(serializers.ModelSerializer):
    status_reason = serializers.SerializerMethodField()
    status_badge = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    class Meta:
        model = WriterStatus
        fields = [
            "id",
            "writer",
            "website",
            "is_active",
            "is_suspended",
            "is_blacklisted",
            "is_on_probation",
            "active_strikes",
            "last_strike_at",
            "suspension_ends_at",
            "probation_ends_at",
            "should_be_suspended",
            "should_be_probated",
            "updated_at",
            "status_reason",
        ]
        read_only_fields = fields

    def get_status_reason(self, obj):
        if obj.is_blacklisted:
            return "Blacklisted by admin."
        if obj.is_suspended:
            return "Suspended for policy violation."
        if obj.should_be_suspended:
            return "Auto-flagged for suspension due to warnings."
        if obj.is_on_probation:
            return "Currently on probation."
        return "Active and in good standing."
    
    def get_status_badge(self, obj):
        if obj.is_blacklisted:
            return "blacklisted"
        if obj.is_suspended:
            return "suspended"
        if obj.should_be_suspended:
            return "flagged"
        if obj.is_on_probation:
            return "probation"
        return "active"

    def get_days_remaining(self, obj):
        if obj.is_suspended and obj.suspension_ends_at:
            delta = obj.suspension_ends_at - now()
            return max(delta.days, 0)
        if obj.is_on_probation and obj.probation_ends_at:
            delta = obj.probation_ends_at - now()
            return max(delta.days, 0)
        return None



class WriterPerformanceSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterPerformanceSnapshot
        fields = "__all__"
        read_only_fields = [
            "writer",
            "website",
            "is_cached",
            "generated_at",
        ]

class WriterPerformanceSummarySerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(
        source="writer.user.get_full_name", read_only=True
    )
    website_name = serializers.CharField(
        source="website.domain", read_only=True
    )

    class Meta:
        model = WriterPerformanceSnapshot
        fields = [
            "writer_name",
            "website_name",
            "period_start",
            "period_end",
            "average_rating",
            "completion_rate",
            "lateness_rate",
            "revision_rate",
            "preferred_order_rate",
            "orders_completed",
            "pages_completed",
            "total_earnings",
            "composite_score",
            "contribution_to_profit",
            "generated_at"
        ]


class WriterLevelSerializer(serializers.ModelSerializer):
    writer_id = serializers.IntegerField(
        source="writer.id", read_only=True
    )
    writer_username = serializers.CharField(
        source="writer.user.username", read_only=True
    )

    class Meta:
        model = WriterLevel
        fields = [
            "id",
            "writer_id",
            "writer_username",
            "level",
            "updated_at",
        ]

class WriterLevelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterLevelHistory
        fields = [
            "id", "level", "changed_at", "triggered_by"
        ]


class WriterWarningSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(
        source='writer.user.username', read_only=True
    )
    issued_by_name = serializers.CharField(
        source='issued_by.username', read_only=True
    )

    class Meta:
        model = WriterWarning
        fields = [
            'id', 'writer', 'writer_name', 'reason',
            'issued_by', 'issued_by_name',
            'issued_at', 'expires_at', 'is_active'
        ]
        read_only_fields = ['issued_by', 'issued_at', 'is_active']

class WriterWarningSelfViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterWarning
        fields = ['reason', 'warning_type', 'created_at', 'expires_at']



class WriterBadgeSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source="badge.name")
    badge_type = serializers.CharField(source="badge.type")
    badge_icon = serializers.CharField(source="badge.icon")

    class Meta:
        model = WriterBadge
        fields = [
            "id", "writer", "badge_name", "badge_type",
            "badge_icon", "issued_at", "is_auto_awarded",
            "revoked", "revoked_reason", "notes"
        ]
        read_only_fields = fields


class WriterBadgeTimelineSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source="badge.name")
    badge_icon = serializers.CharField(source="badge.icon")

    class Meta:
        model = WriterBadge
        fields = [
            "id", "badge_name", "badge_icon",
            "issued_at", "is_auto_awarded"
        ]