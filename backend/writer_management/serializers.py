from rest_framework import serializers
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal
from writer_management.models.order_dispute import OrderDispute
from writer_management.models.webhook_settings import (
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
from writer_management.models.payout import WriterPayment, WriterPayoutPreference, WriterEarningsHistory
from writer_management.models.profile import WriterProfile
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake, WriterDeadlineExtensionRequest,
    WriterOrderHoldRequest, WriterOrderReopenRequest, WriterEarningsReviewRequest
)
try:
    from writer_management.models.pen_name_requests import WriterPenNameChangeRequest
except ImportError:
    WriterPenNameChangeRequest = None
try:
    from writer_management.models.resources import (
        WriterResource, WriterResourceCategory, WriterResourceView
    )
except ImportError:
    WriterResource = None
    WriterResourceCategory = None
    WriterResourceView = None
from writer_management.models.performance import (
    WriterPerformanceReport
)

from writer_management.models.ranking import (
    WriterAutoRanking, WriterRankingCriteria, WriterRankingHistory
)

from writer_management.models.rewards import WriterReward, WriterRewardCriteria
from writer_management.models.status import WriterStatus
from writer_management.models.writer_warnings import WriterWarning

from writer_management.models.tickets import (
    WriterSupportTicket
)
from writer_management.models.discipline import (
    Probation, WriterPenalty, WriterSuspension, WriterStrike,
    WriterStrikeHistory, WriterDisciplineConfig
)
from writer_management.models.logs import (
    WriterActivityLog, WriterIPLog,
    WriterFileDownloadLog
)

from writer_management.models.ratings import WriterRatingCooldown
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
    writer = serializers.PrimaryKeyRelatedField(queryset=WriterProfile.objects.all(), required=False)
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=False)
    order_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = WriterOrderRequest
        fields = '__all__'
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True},
            'reason': {'required': True, 'allow_blank': False}  # Require reason
        }
    
    def validate(self, data):
        """
        Validate that either order or order_id is provided, and reason is provided.
        Also check for basic duplicate prevention (detailed check happens in view).
        """
        if not data.get('order') and not data.get('order_id'):
            raise serializers.ValidationError("Either 'order' or 'order_id' must be provided.")
        
        # Require reason field
        reason = data.get('reason', '').strip()
        if not reason:
            raise serializers.ValidationError({
                'reason': 'Please provide a reason for requesting this order (e.g., your expertise, availability, or interest in the topic).'
            })
        
        # Validate reason length
        if len(reason) < 10:
            raise serializers.ValidationError({
                'reason': 'Please provide a more detailed reason (at least 10 characters).'
            })
        
        if len(reason) > 2000:
            raise serializers.ValidationError({
                'reason': 'Reason is too long (maximum 2000 characters).'
            })
        
        # Convert order_id to order if provided
        if data.get('order_id') and not data.get('order'):
            try:
                data['order'] = Order.objects.get(id=data['order_id'])
            except Order.DoesNotExist:
                raise serializers.ValidationError(f"Order with id {data['order_id']} does not exist.")
        
        # Remove order_id from validated data as it's not a model field
        data.pop('order_id', None)
        
        return data

    def create(self, validated_data):
        if not validated_data.get('website'):
            writer = validated_data.get('writer')
            order = validated_data.get('order')
            website = getattr(writer, 'website', None) or getattr(order, 'website', None)
            if website:
                validated_data['website'] = website
        return super().create(validated_data)


class WriterOrderTakeSerializer(serializers.ModelSerializer):
    """
    Serializer for Writers Taking Orders Directly (If Admin Allows)
    """
    writer = serializers.PrimaryKeyRelatedField(queryset=WriterProfile.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = WriterOrderTake
        fields = '__all__'
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True}
        }

    def validate(self, data):
        """
        Validate if a writer is allowed to take an order based on config and limits.
        Basic validation - detailed checks happen in view with proper locking.
        """
        writer = data.get('writer')
        order = data.get('order')
        
        if not writer:
            raise ValidationError("Writer is required.")
        
        if not order:
            raise ValidationError("Order is required.")
        
        # Check if takes are enabled (basic check, detailed check in view)
        config = WriterConfig.objects.filter(website=writer.website).first()
        if not config or not config.takes_enabled:
            raise ValidationError(
                "Order takes are currently disabled. Writers must request orders."
            )

        # Check if writer is allowed to take orders (admin restriction)
        if not writer.can_take_orders:
            raise ValidationError(
                "You are not allowed to take orders. Please contact an administrator."
            )
        
        # Basic level check
        if not writer.writer_level:
            raise ValidationError(
                "You do not have a writer level assigned. Please contact an administrator."
            )
        
        max_allowed_orders = writer.writer_level.max_orders if writer.writer_level else 0
        
        if max_allowed_orders <= 0:
            raise ValidationError(
                "You do not have permission to take orders. Please contact an administrator."
            )

        return data

    def create(self, validated_data):
        if not validated_data.get('website'):
            writer = validated_data.get('writer')
            order = validated_data.get('order')
            website = getattr(writer, 'website', None) or getattr(order, 'website', None)
            if website:
                validated_data['website'] = website
        return super().create(validated_data)


class WriterConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin-Controlled Writer Settings
    
    Note: max_requests_per_writer and max_takes_per_writer are now managed
    through WriterLevel (Writer Hierarchy) and are read-only here.
    """
    website = serializers.SerializerMethodField()
    
    class Meta:
        model = WriterConfig
        fields = '__all__'
        read_only_fields = ['max_requests_per_writer', 'max_takes_per_writer']
    
    def get_website(self, obj):
        """Get website information"""
        if obj.website:
            return {
                'id': obj.website.id,
                'name': obj.website.name,
                'domain': obj.website.domain,
            }
        return None


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
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        if not validated_data.get('website'):
            writer = validated_data.get('writer')
            if writer is not None:
                website = getattr(writer, 'website', None)
                if website:
                    validated_data['website'] = website
        return super().create(validated_data)


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
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        if not validated_data.get('website'):
            writer = validated_data.get('writer')
            website = getattr(writer, 'website', None)
            if website:
                validated_data['website'] = website
        return super().create(validated_data)


class WriterStrikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Strikes
    """
    writer_username = serializers.CharField(source='writer.user.username', read_only=True)
    writer_email = serializers.CharField(source='writer.user.email', read_only=True)
    issued_by_username = serializers.CharField(source='issued_by.username', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = WriterStrike
        fields = '__all__'
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True},
            'issued_by': {'required': False, 'allow_null': True}
        }
        read_only_fields = ['issued_at']

    def create(self, validated_data):
        if not validated_data.get('website'):
            writer = validated_data.get('writer')
            website = getattr(writer, 'website', None)
            if website:
                validated_data['website'] = website
        if not validated_data.get('issued_by'):
            validated_data['issued_by'] = self.context['request'].user
        return super().create(validated_data)


class WriterStrikeHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Strike History
    """
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = WriterStrikeHistory
        fields = '__all__'
        read_only_fields = ['change_date']


class WriterDisciplineConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer Discipline Configuration
    """
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = WriterDisciplineConfig
        fields = '__all__'
        read_only_fields = ['website_name', 'website_domain']


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
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        if not validated_data.get('website'):
            writer = validated_data.get('writer')
            website = getattr(writer, 'website', None)
            if website:
                validated_data['website'] = website
        return super().create(validated_data)


class WriterDeadlineExtensionRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Deadline Extension Requests
    """
    class Meta:
        model = WriterDeadlineExtensionRequest
        fields = '__all__'
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        if not validated_data.get('website'):
            writer = validated_data.get('writer')
            order = validated_data.get('order')
            website = getattr(writer, 'website', None) or getattr(order, 'website', None)
            if website:
                validated_data['website'] = website
        return super().create(validated_data)


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
    Supports direct tips, order-based tips, and class/task-based tips.
    """
    writer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="writer"), source="writer"
    )
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source="order",
        required=False,
        allow_null=True,
        help_text="Order ID (for order-based tips)"
    )
    related_entity_type = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Type of related entity (e.g., 'class_bundle', 'express_class')"
    )
    related_entity_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID of related entity (for class/task-based tips)"
    )
    tip_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tip_reason = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(
        default='wallet',
        help_text="Payment method: 'wallet', 'stripe', or 'manual'"
    )
    discount_code = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Optional discount code"
    )

    class Meta:
        model = Tip
        fields = [
            "writer_id", "order_id", "related_entity_type", "related_entity_id",
            "tip_amount", "tip_reason", "payment_method", "discount_code"
        ]

    def validate(self, data):
        """
        Validate that either order_id or related_entity info is provided for non-direct tips.
        """
        order = data.get('order')
        related_entity_type = data.get('related_entity_type')
        related_entity_id = data.get('related_entity_id')
        
        # If order is provided, it's order-based
        if order:
            return data
        
        # If related entity info is provided, validate both are present
        if related_entity_type or related_entity_id:
            if not (related_entity_type and related_entity_id):
                raise serializers.ValidationError(
                    "Both related_entity_type and related_entity_id are required for class/task-based tips."
                )
        
        # If neither is provided, it's a direct tip (allowed)
        return data

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
        the writer and the platform, and processing payment.
        """
        from writer_management.services.tip_service import TipService
        request = self.context["request"]
        user = request.user
        website = getattr(request, 'website', None)
        
        # Extract payment-related fields
        payment_method = validated_data.pop('payment_method', 'wallet')
        discount_code = validated_data.pop('discount_code', None)
        
        # Create tip
        tip = TipService.create_tip(
            client=user,
            website=website,
            **validated_data
        )
        
        # Process payment
        if payment_method != 'manual':
            TipService.process_tip_payment(
                tip=tip,
                payment_method=payment_method,
                discount_code=discount_code
            )
        
        return tip
    

class TipListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing tips.
    Writers only see their share, not platform profit or full tip amount.
    """
    writer_name = serializers.CharField(source="writer.get_full_name", read_only=True)
    writer_username = serializers.CharField(source="writer.username", read_only=True)
    client_name = serializers.CharField(source="client.get_full_name", read_only=True)
    client_username = serializers.CharField(source="client.username", read_only=True)
    order_title = serializers.SerializerMethodField()
    related_entity_info = serializers.SerializerMethodField()
    tip_type_display = serializers.CharField(source="get_tip_type_display", read_only=True)
    
    # Writer-safe fields (writers only see their share)
    amount_received = serializers.SerializerMethodField()
    
    class Meta:
        model = Tip
        fields = [
            "id", "tip_type", "tip_type_display", "tip_reason", "sent_at",
            "writer_name", "writer_username", "client_name", "client_username",
            "order_title", "related_entity_info",
            "amount_received",  # Writer sees only their share
            "payment_status",
        ]
    
    def get_order_title(self, obj):
        """Get order title if order-based tip."""
        if obj.order:
            return obj.order.topic or f"Order #{obj.order.id}"
        return None
    
    def get_related_entity_info(self, obj):
        """Get related entity info for class/task-based tips."""
        if obj.related_entity_type and obj.related_entity_id:
            return {
                "type": obj.related_entity_type,
                "id": obj.related_entity_id
            }
        return None
    
    def get_amount_received(self, obj):
        """
        Writers only see their share, not the full tip amount or platform profit.
        Clients and admins see the full tip amount.
        """
        request = self.context.get('request')
        if request and request.user:
            user = request.user
            # Writers only see their share
            if user.role == 'writer' and user == obj.writer:
                return str(obj.writer_earning)
            # Clients and admins see full amount
            elif user.role in ['client', 'admin', 'superadmin']:
                return str(obj.tip_amount)
        # Default: show writer earning (safe default)
        return str(obj.writer_earning)


class TipDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for tip view.
    Writers see only their share; clients/admins see full details.
    """
    writer_name = serializers.CharField(source="writer.get_full_name", read_only=True)
    writer_username = serializers.CharField(source="writer.username", read_only=True)
    client_name = serializers.CharField(source="client.get_full_name", read_only=True)
    client_username = serializers.CharField(source="client.username", read_only=True)
    order_title = serializers.SerializerMethodField()
    related_entity_info = serializers.SerializerMethodField()
    tip_type_display = serializers.CharField(source="get_tip_type_display", read_only=True)
    
    # Conditional fields based on user role
    amount_received = serializers.SerializerMethodField()
    full_tip_amount = serializers.SerializerMethodField()
    writer_percentage_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Tip
        fields = [
            "id", "tip_type", "tip_type_display", "tip_reason", "sent_at",
            "writer_name", "writer_username", "client_name", "client_username",
            "order_title", "related_entity_info",
            "amount_received", "full_tip_amount", "writer_percentage_display",
            "payment_status", "payment",
        ]
    
    def get_order_title(self, obj):
        if obj.order:
            return obj.order.topic or f"Order #{obj.order.id}"
        return None
    
    def get_related_entity_info(self, obj):
        if obj.related_entity_type and obj.related_entity_id:
            return {
                "type": obj.related_entity_type,
                "id": obj.related_entity_id
            }
        return None
    
    def get_amount_received(self, obj):
        """Writer's share (what they receive)."""
        return str(obj.writer_earning)
    
    def get_full_tip_amount(self, obj):
        """Full tip amount (only visible to clients and admins)."""
        request = self.context.get('request')
        if request and request.user:
            user = request.user
            # Writers don't see full amount
            if user.role == 'writer' and user == obj.writer:
                return None
            # Clients and admins see full amount
            elif user.role in ['client', 'admin', 'superadmin']:
                return str(obj.tip_amount)
        return None
    
    def get_writer_percentage_display(self, obj):
        """Writer percentage (only visible to admins)."""
        request = self.context.get('request')
        if request and request.user:
            if request.user.role in ['admin', 'superadmin']:
                return f"{obj.writer_percentage}%"
        return None

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


class WriterPaymentViewSerializer(serializers.Serializer):
    """
    Serializer for writers to view their payment information.
    Shows only level-based payment info (per page, per slide, per class).
    Excludes installments and internal payment details.
    """
    """
    Serializer for writers to view their payment information.
    Shows only level-based payment info (per page, per slide, per class).
    Excludes installments and internal payment details.
    """
    # Level-based payment rates
    cost_per_page = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cost_per_slide = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cost_per_class = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, allow_null=True)
    
    # Current level info
    level_name = serializers.CharField(read_only=True)
    earning_mode = serializers.CharField(read_only=True)
    
    # Order-based earnings (excluding installments)
    order_earnings = serializers.SerializerMethodField()
    
    # Special order earnings
    special_order_earnings = serializers.SerializerMethodField()
    
    # Class bonuses (classes are paid as bonuses, not regular earnings)
    class_bonuses = serializers.SerializerMethodField()
    
    # Totals
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_bonuses = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_tips = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    def get_order_earnings(self, obj):
        """Get earnings from regular orders (excluding installments).
        Uses admin-set writer_compensation if available, otherwise falls back to level-based calculation.
        """
        from orders.models import Order
        from writer_management.services.earnings_calculator import WriterEarningsCalculator
        
        writer_profile = obj
        if not writer_profile.writer_level:
            return []
        
        # Get completed orders assigned to this writer
        orders = Order.objects.filter(
            assigned_writer=writer_profile.user,
            status__in=['completed', 'submitted']
        ).exclude(
            # Exclude orders with installments (special orders with payment plans)
            special_order__isnull=False
        )
        
        earnings = []
        for order in orders:
            # Use admin-set payment amount if available, otherwise calculate from level
            if order.writer_compensation and order.writer_compensation > 0:
                amount = order.writer_compensation
            else:
                # Fallback to level-based calculation
                is_urgent = False
                if order.writer_deadline or order.client_deadline:
                    from django.utils import timezone
                    deadline = order.writer_deadline or order.client_deadline
                    hours_until = (deadline - timezone.now()).total_seconds() / 3600
                    is_urgent = hours_until <= writer_profile.writer_level.urgent_order_deadline_hours
                
                is_technical = getattr(order, 'is_technical', False)
                
                amount = WriterEarningsCalculator.calculate_earnings(
                    writer_profile.writer_level,
                    order,
                    is_urgent=is_urgent,
                    is_technical=is_technical
                )
            
            earnings.append({
                'order_id': order.id,
                'order_topic': order.topic,
                'pages': order.number_of_pages or 0,
                'slides': order.number_of_slides or 0,
                'amount': float(amount),
                'payment_set_by': 'admin' if order.writer_compensation and order.writer_compensation > 0 else 'level',
                'completed_at': order.completed_at.isoformat() if order.completed_at else None,
            })
        
        return earnings
    
    def get_special_order_earnings(self, obj):
        """Get earnings from special orders (excluding installments).
        Uses admin-set payment amount or percentage if available.
        """
        from special_orders.models import SpecialOrder
        from writer_management.services.earnings_calculator import WriterEarningsCalculator
        
        writer_profile = obj
        if not writer_profile.writer_level:
            return []
        
        # Get completed special orders assigned to this writer
        special_orders = SpecialOrder.objects.filter(
            writer=writer_profile.user,
            status='completed'
        )
        
        earnings = []
        for special_order in special_orders:
            # Use admin-set payment amount or percentage if available
            if special_order.writer_payment_amount and special_order.writer_payment_amount > 0:
                # Admin set a fixed amount
                amount = special_order.writer_payment_amount
                payment_set_by = 'admin_amount'
            elif special_order.writer_payment_percentage and special_order.writer_payment_percentage > 0:
                # Admin set a percentage
                order_total = getattr(special_order, 'total_cost', 0) or getattr(special_order, 'admin_approved_cost', 0) or 0
                amount = Decimal(str(order_total)) * (special_order.writer_payment_percentage / Decimal('100'))
                payment_set_by = 'admin_percentage'
            else:
                # Fallback to level-based calculation
                if writer_profile.writer_level.earning_mode == 'fixed_per_page':
                    # Use base pay per page/slide if available
                    amount = (
                        Decimal(str(getattr(special_order, 'number_of_pages', 0) or 0)) * writer_profile.writer_level.base_pay_per_page +
                        Decimal(str(getattr(special_order, 'number_of_slides', 0) or 0)) * writer_profile.writer_level.base_pay_per_slide
                    )
                else:
                    # For percentage modes, use total order amount
                    order_total = getattr(special_order, 'total_cost', 0) or getattr(special_order, 'admin_approved_cost', 0) or 0
                    if writer_profile.writer_level.earning_mode == 'percentage_of_order_cost':
                        amount = Decimal(str(order_total)) * (writer_profile.writer_level.earnings_percentage_of_cost / Decimal('100'))
                    else:
                        amount = Decimal(str(order_total)) * (writer_profile.writer_level.earnings_percentage_of_total / Decimal('100'))
                payment_set_by = 'level'
            
            # Add bonus if available
            bonus = getattr(special_order, 'bonus_amount', 0) or Decimal('0.00')
            
            earnings.append({
                'special_order_id': special_order.id,
                'order_title': getattr(special_order, 'inquiry_details', 'Special Order')[:50],
                'amount': float(amount),
                'bonus': float(bonus),
                'total': float(amount + bonus),
                'payment_set_by': payment_set_by,
                'completed_at': getattr(special_order, 'completed_at', None),
                'completed_at': special_order.updated_at.isoformat() if hasattr(special_order, 'updated_at') and special_order.updated_at else None,
            })
        
        return earnings
    
    def get_class_bonuses(self, obj):
        """Get earnings from classes with streamlined installment details."""
        from class_management.class_payment import ClassPayment
        from special_orders.models import WriterBonus
        
        writer_profile = obj
        if not writer_profile.writer_level:
            return []
        
        # Get class payments using streamlined system
        class_payments = ClassPayment.objects.filter(
            assigned_writer=writer_profile.user
        ).select_related('class_bundle', 'website').prefetch_related(
            'payment_installments__class_installment',
            'writer_payments__writer_bonus'
        )
        
        earnings = []
        for payment in class_payments:
            bundle = payment.class_bundle
            
            # Get installment details
            installments = payment.payment_installments.all()
            installment_details = []
            for inst in installments:
                installment_details.append({
                    'installment_number': inst.installment_number,
                    'amount': float(inst.amount),
                    'is_paid': inst.is_paid,
                    'paid_at': inst.paid_at.isoformat() if inst.paid_at else None,
                })
            
            # Get writer payment status
            writer_payments = payment.writer_payments.all()
            writer_paid = any(wp.is_paid for wp in writer_payments)
            writer_paid_amount = sum(float(wp.amount) for wp in writer_payments if wp.is_paid)
            
            # Hide client payment info from writers - only show their compensation
            earnings.append({
                'bundle_id': bundle.id,
                'class_title': f"Class Bundle #{bundle.id} - {bundle.number_of_classes} classes",
                # DO NOT include total_amount (client payment) - writers shouldn't see this
                'writer_compensation': float(payment.writer_compensation_amount),
                'writer_paid_amount': writer_paid_amount,
                'writer_payment_status': payment.writer_payment_status,
                # DO NOT include client_payment_status - writers shouldn't see this
                # DO NOT include uses_installments, total_installments, paid_installments - client payment details
                # DO NOT include installment_details - client payment details
                # DO NOT include payment_progress - client payment progress
                'is_writer_paid': writer_paid,
                'created_at': payment.created_at.isoformat() if payment.created_at else None,
            })
        
        # Also include legacy WriterBonus records for backward compatibility
        class_bonuses = WriterBonus.objects.filter(
            writer=writer_profile.user,
            category='class_payment'
        ).exclude(
            id__in=[wp.writer_bonus_id for payment in class_payments 
                   for wp in payment.writer_payments.all() if wp.writer_bonus_id]
        )
        
        for bonus in class_bonuses:
            # Hide client payment info - only show writer compensation
            earnings.append({
                'bundle_id': None,
                'class_title': f"Class Bonus - {bonus.reason[:50]}" if bonus.reason else "Class Payment",
                # DO NOT include total_amount - writers shouldn't see client payment
                'writer_compensation': float(bonus.amount),
                'writer_paid_amount': float(bonus.amount) if bonus.is_paid else 0.0,
                'writer_payment_status': 'paid' if bonus.is_paid else 'pending',
                # DO NOT include client_payment_status - writers shouldn't see this
                # DO NOT include installment details - client payment info
                'is_writer_paid': bonus.is_paid,
                'created_at': bonus.granted_at.isoformat() if bonus.granted_at else None,
            })
        
        return earnings



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
    """
    Serializer for WriterLevel (level definitions/templates).
    """
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    writers_count = serializers.SerializerMethodField()
    
    def get_writers_count(self, obj):
        """Get count of writers at this level."""
        return obj.writers.count()
    
    class Meta:
        model = WriterLevel
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'website_name', 'website_domain', 'writers_count']

class WriterLevelConfigSerializer(serializers.ModelSerializer):
    """Serializer for WriterLevelConfig model."""
    website = serializers.PrimaryKeyRelatedField(queryset=Website.objects.all(), required=False, allow_null=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)

    class Meta:
        from writer_management.models.configs import WriterLevelConfig
        model = WriterLevelConfig
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'website_name', 'website_domain']

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


### ---------------- Writer Pen Name & Resources Serializers ---------------- ###

class WriterPenNameChangeRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for pen name change requests.
    """
    writer_username = serializers.CharField(source="writer.user.username", read_only=True)
    writer_registration_id = serializers.CharField(source="writer.registration_id", read_only=True)
    reviewer_username = serializers.CharField(source="reviewed_by.username", read_only=True, allow_null=True)
    
    class Meta:
        model = WriterPenNameChangeRequest
        fields = [
            "id", "website", "writer", "writer_username", "writer_registration_id",
            "current_pen_name", "requested_pen_name", "reason",
            "requested_at", "status", "reviewed_by", "reviewer_username",
            "reviewed_at", "admin_notes"
        ]
        read_only_fields = [
            "id", "requested_at", "status", "reviewed_by", "reviewed_at"
        ]


class WriterResourceCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for writer resource categories.
    """
    resource_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WriterResourceCategory
        fields = [
            "id", "website", "name", "description", "display_order",
            "is_active", "created_at", "updated_at", "resource_count"
        ]
        read_only_fields = ["created_at", "updated_at"]
    
    def get_resource_count(self, obj):
        """Get count of active resources in this category."""
        return obj.resources.filter(is_active=True).count() if hasattr(obj, 'resources') else 0


class WriterResourceSerializer(serializers.ModelSerializer):
    """
    Serializer for writer resources.
    """
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)
    updated_by_username = serializers.CharField(source="updated_by.username", read_only=True, allow_null=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = WriterResource
        fields = [
            "id", "website", "category", "category_name", "title", "description",
            "resource_type", "file", "external_url", "video_url", "content",
            "is_featured", "is_active", "display_order",
            "view_count", "download_count",
            "created_by", "created_by_username", "created_at",
            "updated_by", "updated_by_username", "updated_at",
            "url"
        ]
        read_only_fields = [
            "id", "view_count", "download_count", "created_at", "updated_at"
        ]
    
    def get_url(self, obj):
        """Get the appropriate URL based on resource type."""
        return obj.get_url()


class WriterResourceViewSerializer(serializers.ModelSerializer):
    """
    Serializer for tracking resource views.
    """
    resource_title = serializers.CharField(source="resource.title", read_only=True)
    writer_username = serializers.CharField(source="writer.user.username", read_only=True)
    
    class Meta:
        model = WriterResourceView
        fields = [
            "id", "resource", "resource_title", "writer", "writer_username", "viewed_at"
        ]
        read_only_fields = ["id", "viewed_at"]