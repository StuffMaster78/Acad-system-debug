from rest_framework import serializers
from .models import (
    ClientWallet, ClientWalletTransaction, LoyaltyTransaction,
    LoyaltyPointsConversionConfig
)
from referrals.models import ReferralBonusConfig
from django.utils import timezone

# Serializer for Client Wallet
class ClientWalletSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Get user information"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'username': obj.user.username,
                'first_name': obj.user.first_name or '',
                'last_name': obj.user.last_name or '',
            }
        return None
    
    def get_website(self, obj):
        """Get website information"""
        if obj.website:
            return {
                'id': obj.website.id,
                'name': obj.website.name,
                'domain': obj.website.domain,
            }
        return None
    
    class Meta:
        model = ClientWallet
        fields = [
            'id', 'user', 'website', 'balance', 'currency', 
            'loyalty_points', 
            'last_updated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_updated']

    def update(self, instance, validated_data):
        # Update the wallet fields (balance, loyalty_points)
        instance.balance = validated_data.get('balance', instance.balance)
        instance.loyalty_points = validated_data.get('loyalty_points', instance.loyalty_points)
        instance.save()
        return instance

# Serializer for Client Wallet Transactions (Debit/Credit)
class ClientWalletTransactionSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    is_credit = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientWalletTransaction
        fields = ['id', 'wallet', 'amount', 'transaction_type', 'description', 'created_at', 'reference_id', 'source', 'is_credit']

    def get_source(self, obj):
        """Determine the source of funds based on transaction type"""
        # Client-initiated payments
        if obj.transaction_type in ['top-up']:
            return 'client_payment'
        # Company/admin credits
        elif obj.transaction_type in ['adjustment', 'bonus', 'refund', 'referral_bonus', 'loyalty_conversion']:
            return 'company_credit'
        # Wallet usage (payments)
        elif obj.transaction_type == 'payment':
            return 'wallet_usage'
        else:
            return 'other'
    
    def get_is_credit(self, obj):
        """Check if transaction is a credit (adds to balance)"""
        return obj.amount > 0

    def validate(self, data):
        # Custom validation for amount or any other field
        if data.get('amount', 0) <= 0:
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
    client = serializers.SerializerMethodField()
    referral_balance = serializers.SerializerMethodField()
    referral_bonus_expiration = serializers.SerializerMethodField()
    referral_bonus_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientWallet
        fields = ['id', 'client', 'referral_balance', 'referral_bonus_expiration', 'referral_bonus_percentage']
    
    def get_client(self, obj):
        # Return user information as client
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'username': obj.user.username,
            }
        return None
    
    def get_referral_balance(self, obj):
        # Calculate referral balance from transactions
        # This is a computed field since referral_balance doesn't exist on the model
        from django.db.models import Sum
        referral_transactions = obj.transactions.filter(transaction_type='referral_bonus')
        total = referral_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        return total
    
    def get_referral_bonus_expiration(self, obj):
        # Returning the expiration time in a readable format
        # This field doesn't exist on the model, return None or compute from config
        return None
    
    def get_referral_bonus_percentage(self, obj):
        # This field doesn't exist on the model, return None or get from config
        try:
            from referrals.models import ReferralBonusConfig
            config = ReferralBonusConfig.objects.filter(website=obj.website).first()
            return config.bonus_percentage if config else None
        except:
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
        # Custom logic to calculate total earned bonus from transactions
        from django.db.models import Sum
        referral_transactions = obj.transactions.filter(transaction_type='referral_bonus')
        total = referral_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        return total
    