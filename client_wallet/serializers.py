from rest_framework import serializers
from .models import (
    ClientWallet, ClientWalletTransaction, LoyaltyTransaction,
    ReferralBonusConfig, LoyaltyPointsConversionConfig,
    AdminNotification
)
from django.utils import timezone

# Serializer for Client Wallet
class ClientWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientWallet
        fields = ['id', 'client', 'balance', 'loyalty_points', 'referral_balance', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # Update the wallet fields (balance, loyalty_points, referral_balance)
        instance.balance = validated_data.get('balance', instance.balance)
        instance.loyalty_points = validated_data.get('loyalty_points', instance.loyalty_points)
        instance.referral_balance = validated_data.get('referral_balance', instance.referral_balance)
        instance.save()
        return instance

# Serializer for Client Wallet Transactions (Debit/Credit)
class ClientWalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientWalletTransaction
        fields = ['id', 'client_wallet', 'amount', 'transaction_type', 'description', 'created_at']

    def validate(self, data):
        # Custom validation for amount or any other field
        if data['amount'] <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return data

# Serializer for Loyalty Transactions (Points Conversion)
class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'client_wallet', 'points_deducted', 'transaction_type', 'created_at']

# Serializer for Referral Bonus Configuration
class ReferralBonusConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralBonusConfig
        fields = ['id', 'bonus_percentage', 'bonus_cap', 'bonus_expiry_days', 'created_at', 'updated_at']

    def validate(self, data):
        # Validation for the bonus cap or expiry days, can be customized
        if data['bonus_percentage'] < 0 or data['bonus_percentage'] > 100:
            raise serializers.ValidationError("Bonus percentage must be between 0 and 100")
        if data['bonus_cap'] < 0:
            raise serializers.ValidationError("Bonus cap must be a positive number")
        return data

# Serializer for Loyalty Points Conversion Configuration
class LoyaltyPointsConversionConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyPointsConversionConfig
        fields = ['id', 'conversion_rate', 'min_points_required', 'created_at', 'updated_at']

    def validate(self, data):
        # Validation for minimum points required and conversion rate
        if data['min_points_required'] <= 0:
            raise serializers.ValidationError("Minimum points required must be greater than 0")
        if data['conversion_rate'] <= 0:
            raise serializers.ValidationError("Conversion rate must be greater than 0")
        return data

# Serializer for the Referral Bonus
class ReferralBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientWallet
        fields = ['id', 'client', 'referral_balance', 'referral_bonus_expiration', 'referral_bonus_percentage']

    def get_referral_bonus_expiration(self, obj):
        # Returning the expiration time in a readable format
        expiration = obj.referral_bonus_expiration
        if expiration:
            return expiration.strftime('%Y-%m-%d %H:%M:%S')
        return None

# Serializer for Referral Stats
class ReferralStatsSerializer(serializers.ModelSerializer):
    total_referrals = serializers.IntegerField()
    total_earned_bonus = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = ClientWallet
        fields = ['client', 'total_referrals', 'total_earned_bonus']
    
    def get_total_referrals(self, obj):
        # Custom logic to calculate the total referrals
        return obj.referrals.count()

    def get_total_earned_bonus(self, obj):
        # Custom logic to calculate total earned bonus
        return obj.referral_balance
    
class AdminNotificationSerializer(serializers.ModelSerializer):
    """Serializer for admin notifications."""
    
    class Meta:
        model = AdminNotification
        fields = ["id", "message", "created_at", "is_read"]

    def update(self, instance, validated_data):
        """
        Allows marking a notification as read.
        """
        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.save()
        return instance