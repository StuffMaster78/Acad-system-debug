from rest_framework import serializers
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import (
    WriterProfile, WriterLevel, WriterLeave,
    WriterActionLog, WriterEducation,
    WriterReward, WriterRewardCriteria,
    WriterDemotionRequest, WriterPerformanceReport,
    WriterRating, Probation,
    WriterPenalty, WriterSuspension,
    WriterPayoutPreference, WriterPayment,
    WriterEarningsHistory, WriterEarningsReviewRequest,
    WriterReassignmentRequest, WriterOrderHoldRequest,
    OrderDispute, WriterOrderReopenRequest,
    WriterActivityLog, WriterMessageThread,
    WriterMessage, WriterMessageModeration,
    WriterSupportTicket, WriterDeadlineExtensionRequest,
    WriterAutoRanking, WriterActivityTracking,
    WriterIPLog, WriterRatingCooldown, WriterFileDownloadLog,
    WriterConfig, WriterOrderRequest, WriterOrderTake
)
from orders.models import Order

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
        active_requests = WriterOrderRequest.objects.filter(writer=data['writer'], approved=False).count()

        if active_requests >= max_requests:
            raise ValidationError(f"Writer {data['writer'].user.username} has reached their max request limit.")

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
            raise ValidationError("Order takes are currently disabled. Writers must request orders.")

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