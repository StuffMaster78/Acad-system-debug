from rest_framework import serializers
from .models import (
    Referral, ReferralBonusConfig, ReferralCode, ReferralStats, ReferralBonusDecay
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
    website = WebsiteSerializer(read_only=True)

    class Meta:
        model = ReferralBonusConfig
        fields = [
            'id', 'website', 'first_order_bonus',
            'max_referrals_per_month', 'max_referral_bonus_per_month'
        ]


class ReferralCodeSerializer(serializers.ModelSerializer):
    """Serializer for the ReferralCode model."""
    user = UserSerializer(read_only=True)
    website = WebsiteSerializer(read_only=True)

    class Meta:
        model = ReferralCode
        fields = ['id', 'website', 'user', 'code', 'created_at']
        read_only_fields = ['created_at']

    def get_referral_link(self, obj):
        """Include the referral link in the serialized output."""
        return obj.get_referral_link()


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