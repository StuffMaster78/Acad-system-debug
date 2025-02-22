from rest_framework import serializers
from .models import LoyaltyTier, LoyaltyTransaction, Milestone, ClientBadge


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