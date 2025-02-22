from rest_framework import serializers
from .models import Referral, ReferralBonusConfig, ReferralCode


class ReferralSerializer(serializers.ModelSerializer):
    """
    Serializer for Referral model.
    """
    class Meta:
        model = Referral
        fields = [
            'id', 'referrer', 'referee', 'referral_code', 'created_at',
            'registration_bonus_credited', 'first_order_bonus_credited'
        ]


class ReferralBonusConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for ReferralBonusConfig model.
    """
    class Meta:
        model = ReferralBonusConfig
        fields = [
            'id', 'website', 'registration_bonus', 'first_order_bonus', 'referee_discount'
        ]


class ReferralCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for ReferralCode model.
    """
    class Meta:
        model = ReferralCode
        fields = ['user', 'code', 'created_at']
