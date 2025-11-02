from rest_framework import serializers
from .models import (
    LoyaltyTier, LoyaltyTransaction, Milestone,
    ClientBadge, LoyaltyPointsConversionConfig,
    RedemptionCategory, RedemptionItem, RedemptionRequest,
    LoyaltyAnalytics, DashboardWidget
)
from client_management.models import ClientProfile


class AdminLoyaltyTransferSerializer(serializers.Serializer):
    from_client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all(), source='from_client')
    to_client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all(), source='to_client')
    website_id = serializers.IntegerField()
    points = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=255)

    def validate_points(self, value):
        if value <= 0:
            raise serializers.ValidationError("Points must be greater than zero.")
        return value

    def validate(self, attrs):
        # Additional validation logic can be added here if needed
        return attrs
    
class LoyaltyTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTier
        fields = '__all__'


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.user.username', read_only=True)

    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'client', 'client_username', 'points', 'transaction_type', 'reason', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'


class ClientBadgeSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.user.username', read_only=True)

    class Meta:
        model = ClientBadge
        fields = ['id', 'client', 'client_username', 'badge_name', 'description', 'awarded_at']
        read_only_fields = ['id', 'awarded_at']


class LoyaltyPointsConversionConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for LoyaltyPointsConversionConfig model.
    """
    class Meta:
        model = LoyaltyPointsConversionConfig
        fields = [
            'id', 'website', 'conversion_rate', 'min_conversion_points',
            'max_conversion_limit', 'active'
        ]
        read_only_fields = ['website']

    def validate_conversion_rate(self, value):
        """
        Validate that conversion rate is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Conversion rate must be positive.")
        return value

    def validate_min_conversion_points(self, value):
        """
        Validate that minimum conversion points is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Minimum conversion points must be positive.")
        return value

    def validate_max_conversion_limit(self, value):
        """
        Validate that max conversion limit is not negative.
        """
        if value < 0:
            raise serializers.ValidationError("Maximum conversion limit must be a non-negative value.")
        return value



class LoyaltySummarySerializer(serializers.Serializer):
    loyalty_points = serializers.IntegerField()
    wallet_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    tier = serializers.CharField()
    conversion_rate = serializers.DecimalField(max_digits=6, decimal_places=2)


class LoyaltyConversionSerializer(serializers.Serializer):
    points = serializers.IntegerField()

    def validate_points(self, value):
        if value <= 0:
            raise serializers.ValidationError("Points must be greater than zero.")
        return value

class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'points', 'transaction_type', 'reason', 'created_at']


class LoyaltyTransactionListSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.user.username', read_only=True)

    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'client', 'client_username', 'points', 'transaction_type', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminLoyaltyAwardSerializer(serializers.Serializer):
    client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    website_id = serializers.IntegerField()
    points = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=255)

class AdminLoyaltyForceConvertSerializer(serializers.Serializer):
    client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    website_id = serializers.IntegerField()
    points = serializers.IntegerField(min_value=1)

    def validate_points(self, value):
        if value <= 0:
            raise serializers.ValidationError("Points must be greater than zero.")
        return value

    def validate(self, attrs):
        # Additional validation logic can be added here if needed
        return attrs
    

class AdminLoyaltyDeductSerializer(serializers.Serializer):
    client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all())
    website_id = serializers.IntegerField()
    points = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=255)

    def validate_points(self, value):
        if value <= 0:
            raise serializers.ValidationError("Points must be greater than zero.")
        return value

    def validate(self, attrs):
        # Additional validation logic can be added here if needed
        return attrs
    
class AdminLoyaltyTrasferSerializer(serializers.Serializer):
    from_client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all(), source='from_client')
    to_client_id = serializers.PrimaryKeyRelatedField(queryset=ClientProfile.objects.all(), source='to_client')
    website_id = serializers.IntegerField()
    points = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=255)

    def validate_points(self, value):
        if value <= 0:
            raise serializers.ValidationError("Points must be greater than zero.")
        return value

    def validate(self, attrs):
        # Additional validation logic can be added here if needed
        return attrs    

class AdminLoyaltyTransactionSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.user.username', read_only=True)

    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'client', 'client_username', 'points', 'transaction_type', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


# ============================================================================
# REDEMPTION SYSTEM SERIALIZERS
# ============================================================================

class RedemptionCategorySerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RedemptionCategory
        fields = [
            'id', 'name', 'description', 'is_active', 'sort_order',
            'created_at', 'items_count'
        ]
        read_only_fields = ['created_at']
    
    def get_items_count(self, obj):
        return obj.items.filter(is_active=True).count()


class RedemptionItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    can_redeem = serializers.SerializerMethodField()
    
    class Meta:
        model = RedemptionItem
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'points_required', 'redemption_type', 'discount_code',
            'discount_amount', 'discount_percentage', 'stock_quantity',
            'total_redemptions', 'max_per_client', 'min_tier_level',
            'is_active', 'image_url', 'is_available', 'can_redeem',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_redemptions', 'created_at', 'updated_at']
    
    def get_can_redeem(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                client_profile = request.user.client_profile
                can_redeem, message = obj.can_redeem(client_profile)
                return {'can_redeem': can_redeem, 'message': message}
            except:
                return {'can_redeem': False, 'message': 'Client profile not found'}
        return None


class RedemptionRequestSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_points = serializers.IntegerField(source='item.points_required', read_only=True)
    client_username = serializers.CharField(source='client.user.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True, allow_null=True)
    fulfilled_by_username = serializers.CharField(source='fulfilled_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = RedemptionRequest
        fields = [
            'id', 'item', 'item_name', 'item_points', 'client', 'client_username',
            'points_used', 'status', 'fulfillment_code', 'fulfillment_details',
            'approved_by', 'approved_by_username', 'fulfilled_by', 'fulfilled_by_username',
            'rejection_reason', 'requested_at', 'approved_at', 'fulfilled_at', 'rejected_at'
        ]
        read_only_fields = [
            'id', 'points_used', 'status', 'fulfillment_code', 'fulfillment_details',
            'approved_by', 'fulfilled_by', 'requested_at', 'approved_at',
            'fulfilled_at', 'rejected_at'
        ]


class CreateRedemptionRequestSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    fulfillment_details = serializers.JSONField(required=False, default=dict)


class ApproveRedemptionSerializer(serializers.Serializer):
    redemption_id = serializers.IntegerField()


class RejectRedemptionSerializer(serializers.Serializer):
    redemption_id = serializers.IntegerField()
    reason = serializers.CharField()


# ============================================================================
# ANALYTICS DASHBOARD SERIALIZERS
# ============================================================================

class LoyaltyAnalyticsSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    most_popular_item_name = serializers.CharField(source='most_popular_item.name', read_only=True, allow_null=True)
    
    class Meta:
        model = LoyaltyAnalytics
        fields = [
            'id', 'website', 'website_name', 'date_from', 'date_to',
            'total_active_clients', 'total_points_issued', 'total_points_redeemed',
            'total_points_balance', 'total_redemptions', 'total_redemption_value',
            'most_popular_item', 'most_popular_item_name', 'bronze_count',
            'silver_count', 'gold_count', 'platinum_count',
            'active_redemptions_ratio', 'average_points_per_client',
            'calculated_at', 'updated_at'
        ]
        read_only_fields = ['calculated_at', 'updated_at']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'website', 'website_name', 'widget_type', 'title',
            'position', 'is_visible', 'config', 'created_at'
        ]
        read_only_fields = ['created_at']


class PointsTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    issued = serializers.IntegerField()
    redeemed = serializers.IntegerField()
    balance = serializers.IntegerField()


class TopRedemptionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    points_required = serializers.IntegerField()
    redemption_count = serializers.IntegerField()
    category = serializers.CharField()


class TierDistributionSerializer(serializers.Serializer):
    tier_name = serializers.CharField()
    count = serializers.IntegerField()
    threshold = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class EngagementStatsSerializer(serializers.Serializer):
    total_clients = serializers.IntegerField()
    active_clients = serializers.IntegerField()
    clients_with_redemptions = serializers.IntegerField()
    clients_with_transactions = serializers.IntegerField()
    engagement_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    redemption_rate = serializers.DecimalField(max_digits=5, decimal_places=2)