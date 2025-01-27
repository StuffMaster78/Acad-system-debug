from rest_framework import serializers
from .models import ClientProfile, LoyaltyTransaction


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['client', 'loyalty_points', 'total_spent', 'preferred_writers']


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = ['client', 'points', 'transaction_type', 'timestamp', 'reason']