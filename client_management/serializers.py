from rest_framework import serializers
from .models import (
    ClientProfile,
    LoyaltyPointConfig,
    LoyaltyTransaction,
    LoyaltyPoint,
    LoyaltyPointHistory,
)


class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for ClientProfile model.
    """
    client_username = serializers.CharField(source='client.username', read_only=True)
    preferred_writers = serializers.StringRelatedField(many=True)

    class Meta:
        model = ClientProfile
        fields = [
            'client',
            'client_username',
            'loyalty_points',
            'total_spent',
            'preferred_writers',
        ]


class LoyaltyPointConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for LoyaltyPointConfig model.
    """

    class Meta:
        model = LoyaltyPointConfig
        fields = [
            'points_per_dollar',
            'minimum_points_redeem',
        ]


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for LoyaltyTransaction model.
    """
    client_username = serializers.CharField(source='client.client.username', read_only=True)

    class Meta:
        model = LoyaltyTransaction
        fields = [
            'id',
            'client',
            'client_username',
            'points',
            'transaction_type',
            'timestamp',
            'reason',
        ]


class LoyaltyPointSerializer(serializers.ModelSerializer):
    """
    Serializer for LoyaltyPoint model.
    """
    client_username = serializers.CharField(source='client.username', read_only=True)

    class Meta:
        model = LoyaltyPoint
        fields = [
            'id',
            'client',
            'client_username',
            'points',
            'last_updated',
        ]


class LoyaltyPointHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for LoyaltyPointHistory model.
    """
    client_username = serializers.CharField(source='client.username', read_only=True)

    class Meta:
        model = LoyaltyPointHistory
        fields = [
            'id',
            'client',
            'client_username',
            'points_change',
            'reason',
            'timestamp',
        ]