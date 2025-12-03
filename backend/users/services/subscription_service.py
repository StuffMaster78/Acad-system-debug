"""
Subscription Management Service
Handles subscription operations for clients.
"""
import logging
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models.subscriptions import (
    ClientSubscription,
    SubscriptionPreference,
    SubscriptionType,
    DeliveryChannel
)
from websites.models import Website

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Service for managing client subscriptions.
    """
    
    def __init__(self, user, website: Optional[Website] = None):
        self.user = user
        self.website = website or getattr(user, 'website', None)
        
        if not self.website:
            raise ValidationError("Website is required for subscription management.")
        
        if user.role not in ['client', 'customer']:
            raise ValidationError("Subscriptions are only available for clients.")
    
    def get_or_create_preferences(self) -> SubscriptionPreference:
        """Get or create subscription preferences for the user."""
        preferences, created = SubscriptionPreference.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                'all_subscriptions_enabled': True,
                'email_enabled': True,
                'in_app_enabled': True,
            }
        )
        return preferences
    
    def get_subscription(self, subscription_type: str) -> Optional[ClientSubscription]:
        """Get a specific subscription for the user."""
        try:
            return ClientSubscription.objects.get(
                user=self.user,
                website=self.website,
                subscription_type=subscription_type
            )
        except ClientSubscription.DoesNotExist:
            return None
    
    def get_all_subscriptions(self) -> Dict[str, Any]:
        """Get all subscriptions for the user with their status."""
        subscriptions = ClientSubscription.objects.filter(
            user=self.user,
            website=self.website
        )
        
        result = {}
        for sub_type, _ in SubscriptionType.choices:
            subscription = subscriptions.filter(subscription_type=sub_type).first()
            result[sub_type] = {
                'is_subscribed': subscription.is_subscribed if subscription else False,
                'subscribed_at': subscription.subscribed_at.isoformat() if subscription and subscription.subscribed_at else None,
                'unsubscribed_at': subscription.unsubscribed_at.isoformat() if subscription and subscription.unsubscribed_at else None,
                'frequency': subscription.frequency if subscription else 'immediate',
                'preferred_channels': subscription.preferred_channels if subscription else [],
            }
        
        return result
    
    @transaction.atomic
    def subscribe(self, subscription_type: str, frequency: str = 'immediate', 
                  preferred_channels: Optional[List[str]] = None) -> ClientSubscription:
        """
        Subscribe the user to a subscription type.
        
        Args:
            subscription_type: Type of subscription
            frequency: How frequently to receive messages
            preferred_channels: List of preferred delivery channels
        
        Returns:
            ClientSubscription instance
        """
        if subscription_type not in [choice[0] for choice in SubscriptionType.choices]:
            raise ValidationError(f"Invalid subscription type: {subscription_type}")
        
        # Get or create preferences
        preferences = self.get_or_create_preferences()
        
        # Check if all subscriptions are disabled
        if not preferences.all_subscriptions_enabled:
            raise ValidationError("All subscriptions are currently disabled.")
        
        # For marketing-related subscriptions, check consent
        marketing_types = [
            SubscriptionType.MARKETING_MESSAGES,
            SubscriptionType.PROMOTIONAL_OFFERS,
            SubscriptionType.COUPON_UPDATES,
        ]
        if subscription_type in marketing_types and not preferences.marketing_consent:
            raise ValidationError("Marketing consent is required for this subscription type.")
        
        # Get or create subscription
        subscription, created = ClientSubscription.objects.get_or_create(
            user=self.user,
            website=self.website,
            subscription_type=subscription_type,
            defaults={
                'is_subscribed': True,
                'frequency': frequency,
                'preferred_channels': preferred_channels or [],
            }
        )
        
        if not created:
            subscription.subscribe()
            if frequency:
                subscription.frequency = frequency
            if preferred_channels is not None:
                subscription.preferred_channels = preferred_channels
            subscription.save()
        
        return subscription
    
    @transaction.atomic
    def unsubscribe(self, subscription_type: str) -> ClientSubscription:
        """
        Unsubscribe the user from a subscription type.
        
        Args:
            subscription_type: Type of subscription to unsubscribe from
        
        Returns:
            ClientSubscription instance
        """
        # Transactional messages cannot be unsubscribed
        if subscription_type == SubscriptionType.TRANSACTIONAL_MESSAGES:
            raise ValidationError("Transactional messages cannot be unsubscribed.")
        
        subscription = self.get_subscription(subscription_type)
        if not subscription:
            # Create it as unsubscribed
            subscription = ClientSubscription.objects.create(
                user=self.user,
                website=self.website,
                subscription_type=subscription_type,
                is_subscribed=False,
                unsubscribed_at=timezone.now()
            )
        else:
            subscription.unsubscribe()
        
        return subscription
    
    def update_frequency(self, subscription_type: str, frequency: str) -> ClientSubscription:
        """Update the frequency for a subscription."""
        subscription = self.get_subscription(subscription_type)
        if not subscription or not subscription.is_subscribed:
            raise ValidationError("Subscription not found or not active.")
        
        subscription.frequency = frequency
        subscription.save(update_fields=['frequency', 'updated_at'])
        return subscription
    
    def update_channels(self, subscription_type: str, preferred_channels: List[str]) -> ClientSubscription:
        """Update preferred channels for a subscription."""
        subscription = self.get_subscription(subscription_type)
        if not subscription or not subscription.is_subscribed:
            raise ValidationError("Subscription not found or not active.")
        
        subscription.preferred_channels = preferred_channels
        subscription.save(update_fields=['preferred_channels', 'updated_at'])
        return subscription
    
    def update_preferences(self, **kwargs) -> SubscriptionPreference:
        """
        Update subscription preferences.
        
        Allowed kwargs:
            - all_subscriptions_enabled
            - marketing_consent
            - email_enabled
            - sms_enabled
            - push_enabled
            - in_app_enabled
            - dnd_enabled
            - dnd_start_hour
            - dnd_end_hour
        """
        preferences = self.get_or_create_preferences()
        
        allowed_fields = [
            'all_subscriptions_enabled', 'marketing_consent', 'email_enabled',
            'sms_enabled', 'push_enabled', 'in_app_enabled', 'dnd_enabled',
            'dnd_start_hour', 'dnd_end_hour'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(preferences, field):
                setattr(preferences, field, value)
                if field == 'marketing_consent' and value:
                    preferences.marketing_consent_date = timezone.now()
        
        preferences.save()
        return preferences
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get all subscription preferences."""
        preferences = self.get_or_create_preferences()
        
        return {
            'all_subscriptions_enabled': preferences.all_subscriptions_enabled,
            'marketing_consent': preferences.marketing_consent,
            'marketing_consent_date': preferences.marketing_consent_date.isoformat() if preferences.marketing_consent_date else None,
            'email_enabled': preferences.email_enabled,
            'sms_enabled': preferences.sms_enabled,
            'push_enabled': preferences.push_enabled,
            'in_app_enabled': preferences.in_app_enabled,
            'dnd_enabled': preferences.dnd_enabled,
            'dnd_start_hour': preferences.dnd_start_hour,
            'dnd_end_hour': preferences.dnd_end_hour,
            'transactional_enabled': preferences.transactional_enabled,
        }
    
    def can_receive(self, subscription_type: str, channel: str = 'email') -> bool:
        """
        Check if user can receive a specific subscription type via a channel.
        
        Args:
            subscription_type: Type of subscription
            channel: Delivery channel
        
        Returns:
            True if user can receive, False otherwise
        """
        preferences = self.get_or_create_preferences()
        
        # Check if all subscriptions are disabled
        if not preferences.all_subscriptions_enabled:
            return False
        
        # Transactional messages are always enabled
        if subscription_type == SubscriptionType.TRANSACTIONAL_MESSAGES:
            return True
        
        # Check if subscription is active
        subscription = self.get_subscription(subscription_type)
        if not subscription or not subscription.is_subscribed:
            return False
        
        # Check channel preference
        channel_map = {
            'email': preferences.email_enabled,
            'sms': preferences.sms_enabled,
            'push': preferences.push_enabled,
            'in_app': preferences.in_app_enabled,
        }
        
        if not channel_map.get(channel, False):
            return False
        
        # Check do-not-disturb
        if preferences.dnd_enabled and preferences.is_in_dnd_hours():
            # Only allow critical messages during DND
            critical_types = [
                SubscriptionType.SECURITY_ALERTS,
                SubscriptionType.ORDER_UPDATES,
                SubscriptionType.ACCOUNT_UPDATES,
            ]
            if subscription_type not in critical_types:
                return False
        
        return True

