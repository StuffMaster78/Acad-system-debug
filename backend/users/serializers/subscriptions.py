"""
Serializers for subscription management.
"""
from rest_framework import serializers
from users.models.subscriptions import (
    ClientSubscription,
    SubscriptionPreference,
    SubscriptionType,
    DeliveryChannel
)


class ClientSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for client subscriptions."""
    subscription_type_display = serializers.CharField(
        source='get_subscription_type_display',
        read_only=True
    )
    
    class Meta:
        model = ClientSubscription
        fields = [
            'id',
            'subscription_type',
            'subscription_type_display',
            'is_subscribed',
            'subscribed_at',
            'unsubscribed_at',
            'frequency',
            'preferred_channels',
            'last_sent_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'subscribed_at', 'unsubscribed_at', 
            'last_sent_at', 'created_at', 'updated_at'
        ]


class SubscriptionPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for subscription preferences."""
    
    class Meta:
        model = SubscriptionPreference
        fields = [
            'id',
            'all_subscriptions_enabled',
            'marketing_consent',
            'marketing_consent_date',
            'email_enabled',
            'sms_enabled',
            'push_enabled',
            'in_app_enabled',
            'dnd_enabled',
            'dnd_start_hour',
            'dnd_end_hour',
            'transactional_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'marketing_consent_date', 'created_at', 'updated_at']


class SubscriptionListSerializer(serializers.Serializer):
    """Serializer for listing all available subscriptions."""
    subscription_type = serializers.ChoiceField(choices=SubscriptionType.choices)
    is_subscribed = serializers.BooleanField()
    subscribed_at = serializers.DateTimeField(required=False, allow_null=True)
    unsubscribed_at = serializers.DateTimeField(required=False, allow_null=True)
    frequency = serializers.CharField()
    preferred_channels = serializers.ListField(
        child=serializers.ChoiceField(choices=DeliveryChannel.choices),
        required=False
    )


class SubscribeRequestSerializer(serializers.Serializer):
    """Serializer for subscription requests."""
    subscription_type = serializers.ChoiceField(choices=SubscriptionType.choices)
    frequency = serializers.ChoiceField(
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('monthly', 'Monthly Digest'),
        ],
        default='immediate',
        required=False
    )
    preferred_channels = serializers.ListField(
        child=serializers.ChoiceField(choices=DeliveryChannel.choices),
        required=False,
        allow_empty=True
    )


class UnsubscribeRequestSerializer(serializers.Serializer):
    """Serializer for unsubscription requests."""
    subscription_type = serializers.ChoiceField(choices=SubscriptionType.choices)


class UpdateFrequencySerializer(serializers.Serializer):
    """Serializer for updating subscription frequency."""
    subscription_type = serializers.ChoiceField(choices=SubscriptionType.choices)
    frequency = serializers.ChoiceField(
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('monthly', 'Monthly Digest'),
        ]
    )


class UpdateChannelsSerializer(serializers.Serializer):
    """Serializer for updating preferred channels."""
    subscription_type = serializers.ChoiceField(choices=SubscriptionType.choices)
    preferred_channels = serializers.ListField(
        child=serializers.ChoiceField(choices=DeliveryChannel.choices),
        allow_empty=True
    )

