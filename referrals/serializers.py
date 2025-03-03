from rest_framework import serializers
from .models import Referral, ReferralBonusConfig, ReferralCode


class ReferralSerializer(serializers.ModelSerializer):
    """
    Serializer for the Referral model.
    Displays usernames instead of just IDs.
    """
    referrer = serializers.StringRelatedField()
    referee = serializers.StringRelatedField()
    referral_code = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Referral
        fields = [
            'id', 'referrer', 'referee', 'referral_code', 'created_at',
            'registration_bonus_credited', 'first_order_bonus_credited'
        ]
        read_only_fields = ['created_at', 'registration_bonus_credited', 'first_order_bonus_credited']


class ReferralBonusConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for the ReferralBonusConfig model.
    """
    class Meta:
        model = ReferralBonusConfig
        fields = [
            'id', 'website', 'registration_bonus', 'first_order_bonus', 'referee_discount'
        ]


class ReferralCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for the ReferralCode model with validation.
    """
    code = serializers.CharField(read_only=True)  # Auto-generated, so not user-editable

    class Meta:
        model = ReferralCode
        fields = ['user', 'code', 'created_at']
        read_only_fields = ['created_at']

    def validate_user(self, value):
        """Ensure a user cannot have multiple referral codes"""
        if ReferralCode.objects.filter(user=value).exists():
            raise serializers.ValidationError("User already has a referral code.")
        return value


class ReferralBonusSerializer(serializers.ModelSerializer):
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = WalletTransaction
        fields = ["id", "amount", "expires_at", "time_remaining"]

    def get_time_remaining(self, obj):
        if obj.expires_at:
            delta = obj.expires_at - now()
            return {"days": delta.days, "hours": delta.seconds // 3600}
        return None