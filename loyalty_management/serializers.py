from rest_framework import serializers
from .models import (
    LoyaltyTier, LoyaltyTransaction, Milestone,
    ClientBadge, LoyaltyPointsConversionConfig
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