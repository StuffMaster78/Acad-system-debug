from rest_framework import serializers
from .models import LoyaltyTier, LoyaltyTransaction, Milestone, ClientBadge, LoyaltyPointsConversionConfig


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
