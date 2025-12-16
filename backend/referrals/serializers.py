from rest_framework import serializers
from .models import (
    Referral, ReferralBonusConfig, ReferralCode, ReferralStats, 
    ReferralBonusDecay, ReferralAbuseFlag
)
from users.models import User
from websites.models import Website
from wallet.models import WalletTransaction

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'website', 'email']


class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer for the Website model."""
    class Meta:
        model = Website
        fields = ['id', 'name', 'domain']


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for the Referral model."""
    referrer = UserSerializer(read_only=True)
    referee = UserSerializer(read_only=True)
    website = WebsiteSerializer(read_only=True)

    class Meta:
        model = Referral
        fields = [
            'id', 'referrer', 'website', 'referee',
            'referral_code', 'created_at', 'bonus_awarded'
        ]
        read_only_fields = ['created_at', 'bonus_awarded']


class ReferralBonusConfigSerializer(serializers.ModelSerializer):
    """Serializer for the ReferralBonusConfig model."""
    website = serializers.PrimaryKeyRelatedField(queryset=Website.objects.all(), required=False, allow_null=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)

    class Meta:
        model = ReferralBonusConfig
        fields = [
            'id', 'website', 'website_name', 'website_domain',
            'first_order_bonus', 'first_order_discount_type', 'first_order_discount_amount',
            'bonus_expiry_days', 'max_referrals_per_month', 'max_referral_bonus_per_month'
        ]
        read_only_fields = ['website_name', 'website_domain']


class ReferralCodeSerializer(serializers.ModelSerializer):
    """Serializer for the ReferralCode model."""
    user = UserSerializer(read_only=True)
    website = WebsiteSerializer(read_only=True)
    referral_link = serializers.SerializerMethodField()
    usage_stats = serializers.SerializerMethodField()

    class Meta:
        model = ReferralCode
        fields = [
            'id', 'website', 'user', 'code', 'created_at',
            'referral_link', 'usage_stats'
        ]
        read_only_fields = ['created_at', 'referral_link', 'usage_stats']

    def get_referral_link(self, obj):
        """Include the referral link in the serialized output."""
        return obj.get_referral_link()
    
    def get_usage_stats(self, obj):
        """Get usage statistics for this referral code."""
        from django.db.models import Count, Sum, Q
        from referrals.models import Referral
        
        referrals = Referral.objects.filter(
            referral_code=obj.code,
            website=obj.website
        )
        
        total_referrals = referrals.count()
        successful_referrals = referrals.filter(bonus_awarded=True).count()
        flagged_referrals = referrals.filter(is_flagged=True).count()
        voided_referrals = referrals.filter(is_voided=True).count()
        
        # Get orders placed by referees
        from orders.models import Order
        referee_ids = referrals.values_list('referee_id', flat=True)
        orders_count = Order.objects.filter(
            client_id__in=referee_ids,
            website=obj.website
        ).count()
        
        # Calculate conversion rate
        conversion_rate = (successful_referrals / total_referrals * 100) if total_referrals > 0 else 0
        
        return {
            'total_referrals': total_referrals,
            'successful_referrals': successful_referrals,
            'flagged_referrals': flagged_referrals,
            'voided_referrals': voided_referrals,
            'orders_placed': orders_count,
            'conversion_rate': round(conversion_rate, 2),
            'is_active': obj.user.is_active if obj.user else False,
        }


class ReferralStatsSerializer(serializers.ModelSerializer):
    """Serializer for the ReferralStats model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = ReferralStats
        fields = [
            'id', 'user', 'total_referrals', 'successful_referrals',
            'referral_bonus_earned', 'last_referral_at'
        ]
        read_only_fields = ['last_referral_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for the WalletTransaction model."""
    class Meta:
        model = WalletTransaction
        fields = ['id', 'wallet', 'transaction_type',
                  'amount', 'description', 'website'
        ]


class ReferralAbuseFlagSerializer(serializers.ModelSerializer):
    """Serializer for ReferralAbuseFlag."""
    referral_details = ReferralSerializer(source='referral', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    abuse_type_display = serializers.CharField(source='get_abuse_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReferralAbuseFlag
        fields = '__all__'
        read_only_fields = ['detected_at', 'reviewed_by', 'reviewed_at']


class ReferralAbuseFlagSerializer(serializers.ModelSerializer):
    """Serializer for ReferralAbuseFlag."""
    referral_details = ReferralSerializer(source='referral', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    abuse_type_display = serializers.CharField(source='get_abuse_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReferralAbuseFlag
        fields = '__all__'
        read_only_fields = ['detected_at', 'reviewed_by', 'reviewed_at']


class ReferralBonusDecaySerializer(serializers.ModelSerializer):
    """Serializer for the ReferralBonusDecay model."""
    wallet_transaction = WalletTransactionSerializer(read_only=True)

    class Meta:
        model = ReferralBonusDecay
        fields = ['id', 'wallet_transaction', 'website',
                  'decay_rate', 'decay_start_at'
        ]

    def apply_decay(self, obj):
        """Include the decay calculation in the serialized output."""
        return obj.apply_decay()